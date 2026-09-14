#!/usr/bin/env python3
"""Verify provenance, diversity, integrity and metadata gates for the active pack."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from day4_utils import sha256_file  # noqa: E402


ALLOWED_JPEG_INFO = {"jfif", "jfif_version", "jfif_unit", "jfif_density"}
EXPECTED_ROLES = Counter({"guided": 2, "independent": 8})
EXPECTED_LANES = Counter({"calibration-full-coco17": 2, "cabin-visibility-quality": 8})
EXPECTED_SOURCES = {
    "HSRD-100: 100 High-Quality 3D Human Scans Dataset",
    "Driver Risk Behavior Dataset for Embedded Vision Applications",
    "RGB and Depth videos directory",
}
EXPECTED_LICENSES = {"CC BY 4.0", "CC BY-NC 4.0"}
EXPECTED_SOURCE_COUNTS = Counter(
    {
        "HSRD-100: 100 High-Quality 3D Human Scans Dataset": 2,
        "Driver Risk Behavior Dataset for Embedded Vision Applications": 5,
        "RGB and Depth videos directory": 3,
    }
)


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    manifest = ROOT / "data" / "image-manifest.csv"
    selection_path = ROOT / "data" / "source-selection.json"
    with manifest.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))

    if len(rows) != 10:
        return fail(f"manifest cần đúng 10 row; nhận {len(rows)}")
    participants = [row["participant_code"] for row in rows]
    if len(set(participants)) != 10:
        return fail(f"cần 10 participant_code duy nhất; nhận {len(set(participants))}")
    if Counter(row["role"] for row in rows) != EXPECTED_ROLES:
        return fail("role split phải đúng 2 guided + 8 independent")
    if Counter(row["evidence_lane"] for row in rows) != EXPECTED_LANES:
        return fail("evidence lane phải đúng 2 calibration + 8 cabin")
    if {row["source_dataset"] for row in rows} != EXPECTED_SOURCES:
        return fail("pack phải kết hợp đúng ba nguồn đã duyệt")
    if Counter(row["source_dataset"] for row in rows) != EXPECTED_SOURCE_COUNTS:
        return fail("source split phải đúng HSRD 2 + Mendeley 5 + HADRIAN 3")
    if {row["license_basis"] for row in rows} != EXPECTED_LICENSES:
        return fail("license basis không khớp hai nguồn")
    if {item["participant_code"] for item in selection["images"]} != set(participants):
        return fail("manifest và source-selection lệch participant_code")
    if max(Counter(row["setup_id"] for row in rows).values()) > 3:
        return fail("một setup/camera không được chiếm quá 3 ảnh")

    image_dir = ROOT / "data" / "images"
    expected_files = {row["filename"] for row in rows}
    actual_files = {path.name for path in image_dir.iterdir() if path.is_file()}
    if actual_files != expected_files:
        return fail(
            f"active image set mismatch; missing={sorted(expected_files-actual_files)}, "
            f"unexpected={sorted(actual_files-expected_files)}"
        )

    try:
        for row in rows:
            path = image_dir / row["filename"]
            with Image.open(path) as image:
                image.load()
                if image.format != "JPEG":
                    raise ValueError(f"{path.name} không phải JPEG")
                if image.mode != "RGB":
                    raise ValueError(f"{path.name} phải là RGB")
                if image.size != (int(row["width"]), int(row["height"])):
                    raise ValueError(f"{path.name} dimensions mismatch")
                if len(image.getexif()) != 0:
                    raise ValueError(f"{path.name} còn EXIF")
                unexpected_info = set(image.info) - ALLOWED_JPEG_INFO
                if unexpected_info:
                    raise ValueError(f"{path.name} còn metadata: {sorted(unexpected_info)}")
            if sha256_file(path) != row["sha256"]:
                raise ValueError(f"{path.name} SHA-256 mismatch")
            if row["source_type"] not in {
                "public-real-derived",
                "public-consented-scan-derived",
            }:
                raise ValueError(f"{path.name} sai source_type")
            if row["distribution_status"] != "classroom-noncommercial":
                raise ValueError(f"{path.name} chưa khóa noncommercial lane")
            if not row["privacy_review"].endswith("not-anonymous"):
                raise ValueError(f"{path.name} thiếu privacy boundary")
            if row["evidence_lane"] == "calibration-full-coco17":
                if row["role"] != "guided":
                    raise ValueError(f"{path.name} calibration phải là guided")
                if row["facial_keypoints_scored"] != "yes":
                    raise ValueError(f"{path.name} phải chấm đủ facial keypoints")
                if row["face_evidence"] != "visible-scorable":
                    raise ValueError(f"{path.name} thiếu facial evidence")
                if row["full_body_evidence"] != "visible-scorable":
                    raise ValueError(f"{path.name} thiếu full-body evidence")
            else:
                if row["facial_keypoints_scored"] != "no":
                    raise ValueError(f"{path.name} cabin không được chấm facial keypoints")
                if not row["face_evidence"].endswith("-v0"):
                    raise ValueError(f"{path.name} cabin phải khóa facial nodes ở v=0")
            if all(
                marker not in row["source_behavior_hint"]
                for marker in ("provenance-only", "no state label", "no identity or behaviour ground truth")
            ):
                raise ValueError(f"{path.name} chưa tách source label khỏi ground truth")
            print(
                f"PASS {path.name}: {image.size[0]}x{image.size[1]} "
                f"participant={row['participant_code']} source={row['source_doi']}"
            )
    except (KeyError, OSError, ValueError) as error:
        return fail(str(error))

    print(
        "PASS pack gate: 10 people / 3 sources / 2 full-COCO17 guided + "
        "8 privacy-reduced cabin independent / no AI"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
