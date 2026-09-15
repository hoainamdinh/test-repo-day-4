"""Standard-library validation helpers for the Day 4 COCO-17 pose pilot."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath


KEYPOINT_NAMES = (
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
)

COCO_SKELETON = (
    (16, 14), (14, 12), (17, 15), (15, 13), (12, 13),
    (6, 12), (7, 13), (6, 7), (6, 8), (7, 9),
    (8, 10), (9, 11), (2, 3), (1, 2), (1, 3),
    (2, 4), (3, 5), (4, 6), (5, 7),
)

PILOT_IMAGE_NAMES = (
    "d04-01-calibration-full-coco17-frontal.jpg",
    "d04-02-calibration-raised-arm-coco17.jpg",
    "d04-03-cabin-real-vehicle-baseline.jpg",
    "d04-04-cabin-real-vehicle-object-interaction.jpg",
    "d04-05-cabin-real-vehicle-cool-cast.jpg",
    "d04-06-cabin-real-vehicle-forward-lean.jpg",
    "d04-07-cabin-real-vehicle-handheld-object.jpg",
    "d04-08-cabin-simulator-low-light.jpg",
    "d04-09-cabin-simulator-glare.jpg",
    "d04-10-cabin-simulator-obstruction.jpg",
)

EXPECTED_SUBMISSION_FILES = {
    "COCO_KEYPOINTS_EXPORT.zip",
    "VISIBILITY_REPORT.csv",
    "POSE_REVIEW.md",
}

VISIBILITY_REPORT_COLUMNS = (
    "keypoint_index",
    "keypoint_name",
    "v0_outside_or_unlabeled",
    "v1_occluded",
    "v2_visible",
    "total",
)

MAX_ZIP_MEMBERS = 500
MAX_MEMBER_SIZE = 20 * 1024 * 1024
MAX_TOTAL_SIZE = 100 * 1024 * 1024


class ValidationError(ValueError):
    """Raised when an artifact violates the pilot contract."""


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_members(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = archive.infolist()
    if len(infos) > MAX_ZIP_MEMBERS:
        raise ValidationError(f"ZIP có quá nhiều member: {len(infos)} > {MAX_ZIP_MEMBERS}")

    total_size = 0
    result: dict[str, zipfile.ZipInfo] = {}
    for info in infos:
        raw_name = info.filename.replace("\\", "/")
        path = PurePosixPath(raw_name)
        if path.is_absolute() or ".." in path.parts:
            raise ValidationError(f"ZIP chứa đường dẫn không an toàn: {info.filename}")
        if info.flag_bits & 0x1:
            raise ValidationError(f"ZIP chứa file mã hóa không hỗ trợ: {info.filename}")
        unix_mode = (info.external_attr >> 16) & 0xFFFF
        if unix_mode and stat.S_ISLNK(unix_mode):
            raise ValidationError(f"ZIP chứa symlink không an toàn: {info.filename}")
        if info.file_size > MAX_MEMBER_SIZE:
            raise ValidationError(f"ZIP member quá lớn: {info.filename}")
        total_size += info.file_size
        if total_size > MAX_TOTAL_SIZE:
            raise ValidationError("Tổng kích thước giải nén vượt giới hạn")
        name = path.as_posix().lstrip("./")
        if not name or info.is_dir() or name.startswith("__MACOSX/"):
            continue
        if name in result:
            raise ValidationError(f"ZIP có tên file trùng: {name}")
        result[name] = info
    return result


def _read_coco_json(archive: zipfile.ZipFile, members: dict[str, zipfile.ZipInfo]) -> tuple[str, dict]:
    json_members = [
        (name, info)
        for name, info in members.items()
        if name.casefold().endswith(".json") and not name.casefold().endswith("dataset_meta.json")
    ]
    preferred = [item for item in json_members if "person_keypoints_" in PurePosixPath(item[0]).name]
    candidates = preferred or json_members
    if len(candidates) != 1:
        raise ValidationError(f"Cần đúng một COCO annotation JSON; tìm thấy {len(candidates)}")
    name, info = candidates[0]
    try:
        payload = json.loads(archive.read(info).decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"COCO JSON không phải UTF-8 JSON hợp lệ: {name}") from error
    if not isinstance(payload, dict):
        raise ValidationError("COCO JSON root phải là object")
    return name, payload


def _finite_number(value: object, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{context} phải là số")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValidationError(f"{context} có NaN/Infinity")
    return numeric


def _positive_integer_id(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValidationError(f"{context} phải là integer >= 1")
    return value


def _normalized_skeleton(value: object) -> set[tuple[int, int]]:
    if not isinstance(value, list) or len(value) != len(COCO_SKELETON):
        raise ValidationError("Category skeleton phải có đúng 19 edge")
    edges: set[tuple[int, int]] = set()
    for index, edge in enumerate(value):
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValidationError(f"Category skeleton edge {index} phải có hai node")
        if any(isinstance(node, bool) or not isinstance(node, int) for node in edge):
            raise ValidationError(f"Category skeleton edge {index} phải dùng integer node")
        normalized = tuple(sorted(edge))
        if normalized in edges:
            raise ValidationError("Category skeleton có edge trùng")
        edges.add(normalized)
    return edges


def audit_coco_keypoints_archive(
    archive_path: Path | str,
    expected_image_names: tuple[str, ...] | list[str] = PILOT_IMAGE_NAMES,
) -> dict[str, object]:
    """Audit structural COCO-17 invariants without claiming semantic correctness."""

    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise ValidationError(f"Không tìm thấy COCO ZIP: {archive_path}")
    if not zipfile.is_zipfile(archive_path):
        raise ValidationError(f"Không phải ZIP hợp lệ: {archive_path}")

    with zipfile.ZipFile(archive_path) as archive:
        members = _safe_members(archive)
        bad_member = archive.testzip()
        if bad_member:
            raise ValidationError(f"ZIP lỗi CRC tại: {bad_member}")
        json_member, coco = _read_coco_json(archive, members)

    images = coco.get("images")
    annotations = coco.get("annotations")
    categories = coco.get("categories")
    if not isinstance(images, list) or not isinstance(annotations, list) or not isinstance(categories, list):
        raise ValidationError("COCO cần arrays images, annotations và categories")
    if len(categories) != 1 or not isinstance(categories[0], dict):
        raise ValidationError("COCO pilot cần đúng một category person")

    category = categories[0]
    if category.get("name") != "person":
        raise ValidationError("Category phải có name=person")
    if tuple(category.get("keypoints", ())) != KEYPOINT_NAMES:
        raise ValidationError("Category keypoints sai tên hoặc thứ tự COCO-17")
    skeleton = _normalized_skeleton(category.get("skeleton"))
    expected_skeleton = {tuple(sorted(edge)) for edge in COCO_SKELETON}
    if skeleton != expected_skeleton:
        raise ValidationError("Category skeleton phải đúng 19 edge COCO")

    expected_names = tuple(expected_image_names)
    if len(expected_names) != len(set(expected_names)):
        raise ValidationError("Expected image names có tên trùng")

    image_by_id: dict[object, dict] = {}
    actual_names: list[str] = []
    for index, image in enumerate(images):
        if not isinstance(image, dict):
            raise ValidationError(f"images[{index}] phải là object")
        image_id = _positive_integer_id(image.get("id"), f"images[{index}].id")
        if image_id in image_by_id:
            raise ValidationError(f"images[{index}] trùng id")
        name = PurePosixPath(str(image.get("file_name", "")).replace("\\", "/")).name
        if not name:
            raise ValidationError(f"images[{index}] thiếu file_name")
        width = _finite_number(image.get("width"), f"images[{index}].width")
        height = _finite_number(image.get("height"), f"images[{index}].height")
        if width <= 0 or height <= 0:
            raise ValidationError(f"images[{index}] dimensions phải dương")
        image_by_id[image_id] = image
        actual_names.append(name)
    if sorted(actual_names) != sorted(expected_names):
        raise ValidationError(
            f"Image basename mismatch; expected {sorted(expected_names)}, nhận {sorted(actual_names)}"
        )
    if len(actual_names) != len(set(actual_names)):
        raise ValidationError("COCO images có basename trùng")

    category_id = _positive_integer_id(category.get("id"), "categories[0].id")
    annotation_ids: set[object] = set()
    annotations_per_image = {image_id: 0 for image_id in image_by_id}
    visibility_counts = [{0: 0, 1: 0, 2: 0} for _ in KEYPOINT_NAMES]
    warnings: list[str] = [
        "Structural PASS không chứng minh vị trí giải phẫu, left/right hoặc visibility decision đúng."
    ]

    for index, annotation in enumerate(annotations):
        if not isinstance(annotation, dict):
            raise ValidationError(f"annotations[{index}] phải là object")
        annotation_id = _positive_integer_id(annotation.get("id"), f"annotations[{index}].id")
        if annotation_id in annotation_ids:
            raise ValidationError(f"annotations[{index}] trùng id")
        annotation_ids.add(annotation_id)
        image_id = _positive_integer_id(annotation.get("image_id"), f"annotations[{index}].image_id")
        if image_id not in image_by_id:
            raise ValidationError(f"annotations[{index}] tham chiếu image_id không tồn tại")
        if annotation.get("category_id") != category_id:
            raise ValidationError(f"annotations[{index}] sai category_id")
        annotations_per_image[image_id] += 1

        keypoints = annotation.get("keypoints")
        if not isinstance(keypoints, list) or len(keypoints) != len(KEYPOINT_NAMES) * 3:
            raise ValidationError(f"annotations[{index}].keypoints phải có đúng 51 số")
        visible_count = 0
        image = image_by_id[image_id]
        width, height = float(image["width"]), float(image["height"])
        for keypoint_index, name in enumerate(KEYPOINT_NAMES):
            x = _finite_number(keypoints[keypoint_index * 3], f"{annotation_id}.{name}.x")
            y = _finite_number(keypoints[keypoint_index * 3 + 1], f"{annotation_id}.{name}.y")
            visibility_raw = keypoints[keypoint_index * 3 + 2]
            visibility = _finite_number(visibility_raw, f"{annotation_id}.{name}.v")
            if not visibility.is_integer() or int(visibility) not in {0, 1, 2}:
                raise ValidationError(f"{annotation_id}.{name}.v phải là 0, 1 hoặc 2")
            visibility_int = int(visibility)
            visibility_counts[keypoint_index][visibility_int] += 1
            if visibility_int > 0:
                visible_count += 1
                if not (0 <= x <= width and 0 <= y <= height):
                    raise ValidationError(f"{annotation_id}.{name} v>0 nhưng tọa độ ngoài ảnh")

        num_keypoints = annotation.get("num_keypoints")
        if isinstance(num_keypoints, bool) or not isinstance(num_keypoints, int):
            raise ValidationError(f"annotations[{index}].num_keypoints phải là integer")
        if num_keypoints != visible_count:
            raise ValidationError(
                f"annotations[{index}].num_keypoints={num_keypoints}, count(v>0)={visible_count}"
            )
        bbox = annotation.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise ValidationError(f"annotations[{index}].bbox phải có bốn số")
        bbox_values = [_finite_number(value, f"annotations[{index}].bbox") for value in bbox]
        if bbox_values[2] <= 0 or bbox_values[3] <= 0:
            raise ValidationError(f"annotations[{index}].bbox width/height phải dương")

    wrong_counts = [image_id for image_id, count in annotations_per_image.items() if count != 1]
    if wrong_counts:
        raise ValidationError("Pilot cần đúng một person annotation trên mỗi image")

    rows = []
    for index, (name, counts) in enumerate(zip(KEYPOINT_NAMES, visibility_counts)):
        rows.append(
            {
                "keypoint_index": index,
                "keypoint_name": name,
                "v0_outside_or_unlabeled": counts[0],
                "v1_occluded": counts[1],
                "v2_visible": counts[2],
                "total": sum(counts.values()),
            }
        )

    return {
        "archive": archive_path.name,
        "sha256": sha256_file(archive_path),
        "annotation_json_member": json_member,
        "image_count": len(images),
        "annotation_count": len(annotations),
        "keypoint_count": len(KEYPOINT_NAMES),
        "visibility_rows": rows,
        "semantic_review_required": True,
        "warnings": warnings,
    }


def write_visibility_report(report: dict[str, object], output_path: Path | str) -> Path:
    output_path = Path(output_path)
    rows = report.get("visibility_rows")
    if not isinstance(rows, list) or len(rows) != len(KEYPOINT_NAMES):
        raise ValidationError("Audit report không có đủ visibility rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=VISIBILITY_REPORT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def validate_visibility_report(path: Path | str, expected_rows: list[dict[str, object]]) -> None:
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"Không tìm thấy {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != VISIBILITY_REPORT_COLUMNS:
            raise ValidationError("VISIBILITY_REPORT.csv sai header hoặc thứ tự cột")
        actual_rows = list(reader)
    normalized_expected = [{key: str(row[key]) for key in VISIBILITY_REPORT_COLUMNS} for row in expected_rows]
    if actual_rows != normalized_expected:
        raise ValidationError("VISIBILITY_REPORT.csv không khớp COCO export hiện tại")


def validate_pose_review(path: Path | str, expected_image_names: tuple[str, ...] = PILOT_IMAGE_NAMES) -> None:
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"Không tìm thấy {path.name}")
    text = path.read_text(encoding="utf-8-sig")
    for marker in ("SELF_QC_COMPLETE: yes", "PEER_REVIEW_COMPLETE: yes", "REWORK_COMPLETE: yes"):
        if marker not in text:
            raise ValidationError(f"POSE_REVIEW.md thiếu marker: {marker}")
    for image_name in expected_image_names:
        if image_name not in text:
            raise ValidationError(f"POSE_REVIEW.md thiếu evidence cho {image_name}")
    if re.search(r"\bTODO\b", text, re.IGNORECASE):
        raise ValidationError("POSE_REVIEW.md còn TODO")


def validate_submission_directory(directory: Path | str) -> dict[str, object]:
    directory = Path(directory)
    if not directory.is_dir():
        raise ValidationError(f"Không tìm thấy submission directory: {directory}")
    actual_files = {path.name for path in directory.iterdir() if path.is_file() and not path.name.startswith(".")}
    if actual_files != EXPECTED_SUBMISSION_FILES:
        raise ValidationError(
            f"Submission root phải có đúng {sorted(EXPECTED_SUBMISSION_FILES)}; nhận {sorted(actual_files)}"
        )
    report = audit_coco_keypoints_archive(directory / "COCO_KEYPOINTS_EXPORT.zip")
    validate_visibility_report(directory / "VISIBILITY_REPORT.csv", report["visibility_rows"])
    validate_pose_review(directory / "POSE_REVIEW.md")
    return {
        "files": sorted(actual_files),
        "export_sha256": report["sha256"],
        "structural_pass": True,
        "semantic_review_required": True,
    }


def package_submission(directory: Path | str, output_path: Path | str) -> tuple[Path, dict[str, object]]:
    directory = Path(directory)
    output_path = Path(output_path)
    report = validate_submission_directory(directory)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(EXPECTED_SUBMISSION_FILES):
            archive.write(directory / name, arcname=name)
    return output_path, report
