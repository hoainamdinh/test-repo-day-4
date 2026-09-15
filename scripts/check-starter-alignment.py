#!/usr/bin/env python3
"""Kiểm technical compatibility baseline giữa pilot Day 4 và repo starter.

Starter là **baseline kỹ thuật**, không phải quyền quyết định lab: script này chỉ kiểm
tương thích (schema, định dạng, asset, toolchain), không kiểm và không áp đặt timeline,
learning objective hay rubric — những thứ đó do owner của pilot quyết.

Chỉ dùng thư viện chuẩn. Kiểm ba chiều:
  - starter còn đúng hình dạng mà pilot giả định (ảnh, nhãn, schema, tool, asset, notebook);
  - checkout đang ở đúng commit đã pin (trừ khi chạy với --allow-unpinned);
  - hai lane không bị trộn (gate G-05 trong STARTER_ALIGNMENT.md).

    python3 scripts/check-starter-alignment.py --starter ../tmp/day4-starter
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Commit starter mà bản alignment hiện tại đã được xác minh. Đổi giá trị này là một
# quyết định có chủ ý: phải chạy lại T-02 và cập nhật STARTER_ALIGNMENT.md + PILOT_RUN_SHEET.md.
PINNED_STARTER_COMMIT = "79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3"

KEYPOINT_NAMES = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)
FLIP_IDX = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
VALUES_PER_LINE = 5 + 3 * len(KEYPOINT_NAMES)
STARTER_TOOLS = (
    "coco_kp_to_yolo_pose.py",
    "check_pose_labels.py",
    "visibility_report.py",
    "visualize_pose.py",
    "evaluate_pose_annotations.py",
    "poselib.py",
)
# Ba skeleton label mà task A (person) và task B (hand+face) cần.
SKELETON_SUBLABEL_COUNTS = {"person": 17, "hand": 21, "face": 5}
SKELETON_SVG_NAMES = ("skeleton_person_17.svg", "skeleton_hand_21.svg", "skeleton_face_5.svg")
LABELS_SPEC_NAME = "labels_day4.json"
GOLD_MARKER = "labels/train"


class Checker:
    """Thu kết quả từng check để in một bảng và trả về đúng một exit code."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.notes: list[str] = []

    def check(self, name: str, ok: bool, detail: str = "") -> bool:
        print(f"{'PASS' if ok else 'FAIL'}  {name}{f' — {detail}' if detail else ''}")
        if not ok:
            self.failures.append(name)
        return ok

    def note(self, message: str) -> None:
        print(f"NOTE  {message}")
        self.notes.append(message)


def find_starter_assets_dir(starter: Path) -> Path | None:
    """$STARTER_ASSETS_DIR — thư mục chứa label specification của skeleton."""
    matches = sorted(starter.rglob(LABELS_SPEC_NAME))
    return matches[0].parent if matches else None


def find_gold_release_dir(starter: Path) -> Path | None:
    """$GOLD_RELEASE_DIR — thư mục gold được bảo vệ, chỉ phát sau khi nhãn đã khoá.

    Tìm theo hình dạng (`gold/labels/train` có file .txt) chứ không theo vị trí cố định,
    để không phụ thuộc cách starter sắp xếp thư mục.
    """
    for candidate in sorted(starter.rglob("gold")):
        if candidate.is_dir() and any((candidate / GOLD_MARKER).glob("*.txt")):
            return candidate
    return None


def parse_label_file(path: Path) -> list[list[float]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != VALUES_PER_LINE:
            raise ValueError(f"{path.name}:{line_number}: {len(parts)} số, cần {VALUES_PER_LINE}")
        values = [float(part) for part in parts]
        for index in range(len(KEYPOINT_NAMES)):
            if values[7 + index * 3] not in (0.0, 1.0, 2.0):
                raise ValueError(f"{path.name}:{line_number}: cờ visibility ngoài {{0,1,2}}")
        rows.append(values)
    return rows


def check_commit_pin(starter: Path, checker: Checker, allow_unpinned: bool) -> None:
    result = subprocess.run(
        ["git", "-C", str(starter), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        checker.check(
            "checkout starter có metadata git để đối chiếu commit pin",
            allow_unpinned,
            "không đọc được HEAD; chạy lại với --allow-unpinned nếu đây là bản tải ZIP",
        )
        return
    head = result.stdout.strip()
    if allow_unpinned:
        checker.note(f"bỏ qua commit pin theo yêu cầu — HEAD = {head}")
        return
    checker.check(
        "checkout starter đúng commit đã pin",
        head == PINNED_STARTER_COMMIT,
        f"HEAD {head} ≠ pin {PINNED_STARTER_COMMIT}; chạy lại T-02 rồi cập nhật pin"
        if head != PINNED_STARTER_COMMIT else "",
    )


def check_dataset(starter: Path, checker: Checker) -> None:
    train_images = sorted((starter / "dataset/images/train").glob("*.jpg"))
    test_images = sorted((starter / "dataset/images/test").glob("*.jpg"))
    checker.check("20 ảnh train", len(train_images) == 20, f"{len(train_images)} ảnh")
    checker.check("10 ảnh test", len(test_images) == 10, f"{len(test_images)} ảnh")

    train_labels = sorted((starter / "dataset/labels/train").glob("*.txt"))
    checker.check(
        "nhãn train trống khi pull", not train_labels,
        "có nhãn sẵn — đây là bản đã làm, không phải bản phát cho người học" if train_labels else "",
    )

    test_labels = sorted((starter / "dataset/labels/test").glob("*.txt"))
    checker.check("10 file nhãn test", len(test_labels) == 10, f"{len(test_labels)} file")
    try:
        people = sum(len(parse_label_file(path)) for path in test_labels)
        checker.check("nhãn test đúng 56 số/dòng", True, f"{people} người")
    except ValueError as error:
        checker.check("nhãn test đúng 56 số/dòng", False, str(error))


def check_data_yaml(starter: Path, checker: Checker) -> None:
    path = starter / "data.yaml"
    if not checker.check("có data.yaml", path.is_file()):
        return
    text = path.read_text(encoding="utf-8")
    shape = re.search(r"^kpt_shape:\s*\[\s*17\s*,\s*3\s*\]", text, re.M)
    checker.check("kpt_shape: [17, 3]", bool(shape), "" if shape else "cờ visibility bị vứt")
    flip = re.search(r"^flip_idx:\s*\[([^\]]+)\]", text, re.M)
    parsed = [int(value) for value in flip.group(1).split(",")] if flip else []
    checker.check("flip_idx khớp COCO-17", parsed == FLIP_IDX, str(parsed) if parsed != FLIP_IDX else "")
    checker.check("val trỏ tập test", "val: dataset/images/test" in text)


def check_toolchain(starter: Path, checker: Checker) -> None:
    missing = [name for name in STARTER_TOOLS if not (starter / "tools" / name).is_file()]
    checker.check(f"đủ {len(STARTER_TOOLS)} tool chấm", not missing, ", ".join(missing))

    evaluator = starter / "tools/evaluate_pose_annotations.py"
    if evaluator.is_file():
        source = evaluator.read_text(encoding="utf-8")
        findings = {name for name in re.findall(r"['\"](dao_trai_phai|nham_nguoi|xoa_khop_bi_che)['\"]", source)}
        checker.check(
            "evaluator còn sinh đủ 3 loại finding pilot dựa vào",
            findings == {"dao_trai_phai", "nham_nguoi", "xoa_khop_bi_che"},
            f"thấy {sorted(findings)}" if findings != {"dao_trai_phai", "nham_nguoi", "xoa_khop_bi_che"} else "",
        )
        checker.check("evaluator dùng OKS", "oks" in source.casefold())

    poselib = (starter / "tools/poselib.py").read_text(encoding="utf-8") if (starter / "tools/poselib.py").is_file() else ""
    names_in_order = re.findall(r'"([a-z_]+)"', poselib.split("NUM_KEYPOINTS")[0])
    checker.check(
        "thứ tự 17 keypoint của starter trùng schema pilot",
        tuple(names_in_order[: len(KEYPOINT_NAMES)]) == KEYPOINT_NAMES,
    )

    notebooks = sorted((starter / "notebooks").glob("*.ipynb"))
    checker.check("có notebook fine-tune", bool(notebooks), ", ".join(path.name for path in notebooks))
    for notebook in notebooks:
        source = notebook.read_text(encoding="utf-8")
        model = re.search(r"MODEL_NAME = '([^']+)'", source)
        if model:
            checker.note(f"{notebook.name}: MODEL_NAME = {model.group(1)} (quyết định model là của owner — G-04)")
        if "install -U ultralytics" in source:
            checker.note(f"{notebook.name}: cài ultralytics không pin version (D-05)")


def check_skeleton_assets(starter: Path, checker: Checker) -> None:
    """Asset dựng skeleton cho cả hai task: A (person 17) và B (hand 21 + face 5)."""
    assets_dir = find_starter_assets_dir(starter)
    if not checker.check(
        f"thấy $STARTER_ASSETS_DIR (chứa {LABELS_SPEC_NAME})",
        assets_dir is not None,
        assets_dir.relative_to(starter).as_posix() if assets_dir else "không tìm thấy",
    ):
        return

    try:
        labels = json.loads((assets_dir / LABELS_SPEC_NAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        checker.check(f"đọc được {LABELS_SPEC_NAME}", False, str(error))
        return

    counts = {
        entry.get("name"): len(entry.get("sublabels", []))
        for entry in labels
        if entry.get("type") == "skeleton"
    }
    checker.check(
        "đủ 3 skeleton label 17/21/5 (task A person, task B hand+face)",
        counts == SKELETON_SUBLABEL_COUNTS,
        f"thấy {counts}" if counts != SKELETON_SUBLABEL_COUNTS else "",
    )

    person = next((entry for entry in labels if entry.get("name") == "person"), None)
    if person:
        names = tuple(sub.get("name") for sub in person.get("sublabels", []))
        checker.check("thứ tự 17 sublabel của `person` trùng schema pilot", names == KEYPOINT_NAMES)

    missing_svg = [name for name in SKELETON_SVG_NAMES if not (assets_dir / name).is_file()]
    checker.check("đủ 3 skeleton SVG để upload qua Configurator", not missing_svg, ", ".join(missing_svg))


def check_schema_match(starter: Path, checker: Checker) -> None:
    schema = json.loads((ROOT / "data/schema/coco17-keypoints.json").read_text(encoding="utf-8"))
    checker.check("schema pilot đúng 17 tên COCO", tuple(schema["keypoints"]) == KEYPOINT_NAMES)
    checker.check("schema pilot đúng flip_idx", schema["flip_idx"] == FLIP_IDX)

    poselib = starter / "tools/poselib.py"
    if not poselib.is_file():
        return
    block = poselib.read_text(encoding="utf-8").split("SKELETON = [")[-1].split("]")[0]
    starter_edges = {tuple(sorted(map(int, pair))) for pair in re.findall(r"\((\d+),\s*(\d+)\)", block)}
    pilot_edges = {tuple(sorted(value - 1 for value in edge)) for edge in schema["skeleton"]}
    checker.check(
        "19 cạnh skeleton trùng nhau (starter 0-indexed, pilot 1-indexed)",
        starter_edges == pilot_edges,
        f"lệch: {sorted(starter_edges ^ pilot_edges)}" if starter_edges != pilot_edges else "",
    )


def check_lane_separation(starter: Path, checker: Checker) -> None:
    cabin_names = {path.name for path in (ROOT / "data/images").glob("*.jpg")}
    leaked = [
        path.name
        for path in (starter / "dataset").rglob("*")
        if path.is_file() and path.name in cabin_names
    ]
    checker.check("G-05a: không có ảnh cabin trong dataset starter", not leaked, ", ".join(leaked))

    protected_in_pilot = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and ("gold" in path.parts or path.name in {"person_keypoints_train.json", "manifest.json"})
    ]
    checker.check(
        "G-05b: không có gold/manifest của starter trong pilot",
        not protected_in_pilot,
        ", ".join(protected_in_pilot),
    )

    gold_dir = find_gold_release_dir(starter)
    if gold_dir is None:
        checker.note("checkout này không kèm $GOLD_RELEASE_DIR — đúng với bản phát cho người học")
        return

    checker.note(
        f"checkout này có $GOLD_RELEASE_DIR ({gold_dir.relative_to(starter).as_posix()}) — "
        "bản phát cho người học phải không có nó, và nó chỉ được mở sau khi nhãn đã khoá"
    )
    gold_labels = sorted((gold_dir / GOLD_MARKER).glob("*.txt"))
    try:
        people = sum(len(parse_label_file(path)) for path in gold_labels)
        checker.check(
            "gold train có 29 người trên 20 ảnh",
            people == 29 and len(gold_labels) == 20,
            f"{people} người / {len(gold_labels)} file",
        )
    except ValueError as error:
        checker.check("gold train đọc được", False, str(error))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--starter", type=Path, required=True, help="đường dẫn checkout repo starter")
    parser.add_argument(
        "--allow-unpinned",
        action="store_true",
        help=f"cho phép chạy trên commit khác {PINNED_STARTER_COMMIT[:12]} (bản ZIP, hoặc đang khảo sát commit mới)",
    )
    args = parser.parse_args()

    starter = args.starter.resolve()
    checker = Checker()
    if not checker.check("thấy checkout starter", (starter / "data.yaml").is_file() or starter.is_dir(), str(starter)):
        return 1
    if not (starter / "data.yaml").is_file():
        print(f"FAIL  không thấy data.yaml trong {starter}", file=sys.stderr)
        return 1

    check_commit_pin(starter, checker, args.allow_unpinned)
    check_dataset(starter, checker)
    check_data_yaml(starter, checker)
    check_toolchain(starter, checker)
    check_skeleton_assets(starter, checker)
    check_schema_match(starter, checker)
    check_lane_separation(starter, checker)

    print()
    if checker.failures:
        print(f"FAIL {len(checker.failures)} check: {', '.join(checker.failures)}", file=sys.stderr)
        return 1
    print("PASS toàn bộ bất biến compatibility. Gate G-01..G-04, G-06 vẫn cần chạy tay.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
