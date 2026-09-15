#!/usr/bin/env python3
"""Chấm cả lớp trong một lệnh: mỗi bài nộp là một ZIP export COCO Keypoints 1.0 của CVAT.

Học viên vẫn nộp đúng thứ CVAT xuất ra, không phải convert tay. Script làm hộ toàn bộ
chuỗi cho từng ZIP:

    ZIP → kiểm cấu trúc COCO-17 → tools/coco_kp_to_yolo_pose.py → nhãn YOLO .txt
        → tools/evaluate_pose_annotations.py (OKS với gold) → một dòng trong bảng tổng

Kết quả ra `summary.csv` + `summary.md` kèm JSON chi tiết của từng bài, mặc định ghi vào
`outputs/grading/` (thư mục này đã nằm trong .gitignore nên số liệu chấm không lọt vào git).

Script **không fork** toolchain của starter: nó gọi `tools/*.py` tại chỗ, nên OKS và cách
gọi tên lỗi chỉ có một định nghĩa duy nhất.

    python3 scripts/grade-batch.py --submissions ~/baithu --starter ../tmp/day4-starter

Lane C (10 ảnh cabin, không có gold) chỉ kiểm được cấu trúc:

    python3 scripts/grade-batch.py --submissions ~/baithu --lane C
"""

import argparse
import csv
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from day4_utils import (  # noqa: E402
    PILOT_IMAGE_NAMES,
    ValidationError,
    audit_coco_keypoints_archive,
)

GOLD_MARKER = "labels/train"
CONVERTER = "tools/coco_kp_to_yolo_pose.py"
EVALUATOR = "tools/evaluate_pose_annotations.py"

# Thang ba mức của starter; giữ nguyên ngưỡng để pilot không đẻ ra thang thứ hai.
LEVELS = (("Xuất sắc", 0.85, 0.85), ("Đạt", 0.75, 0.70), ("Cần rework", 0.0, 0.0))

# Bốn lỗi được đọc tên trong bảng tổng; phần còn lại vẫn nằm đủ trong JSON chi tiết.
HEADLINE_FINDINGS = ("dao_trai_phai", "nham_nguoi", "thieu_nguoi", "xoa_khop_bi_che")

CSV_COLUMNS = (
    "student", "structure", "mean_oks", "oks50", "oks75", "level",
    "matched_people", "missing_people", "extra_people",
    *HEADLINE_FINDINGS, "note",
)


def find_gold_dir(starter: Path) -> Path | None:
    """Tìm $GOLD_RELEASE_DIR theo hình dạng thư mục, giống check-starter-alignment.py."""
    for candidate in sorted(starter.rglob("gold")):
        if candidate.is_dir() and any((candidate / GOLD_MARKER).glob("*.txt")):
            return candidate
    return None


def starter_image_names(starter: Path) -> tuple[str, ...]:
    images = sorted((starter / "dataset/images/train").glob("*.*"))
    return tuple(path.name for path in images)


def level_of(mean_oks: float, oks75: float) -> str:
    for name, oks_floor, strict_floor in LEVELS:
        if mean_oks >= oks_floor and oks75 >= strict_floor:
            return name
    return LEVELS[-1][0]


def extract_coco_json(archive_path: Path, member: str, target_dir: Path) -> Path:
    """Lấy đúng file .json đã được audit xác nhận, không giải nén cả ZIP."""
    with zipfile.ZipFile(archive_path) as archive:
        data = archive.read(member)
    target = target_dir / "person_keypoints.json"
    target.write_bytes(data)
    return target


def run_tool(starter: Path, tool: str, arguments: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(starter / tool), *arguments],
        cwd=starter, capture_output=True, text=True,
    )


def grade_one(
    archive_path: Path,
    starter: Path | None,
    gold_dir: Path | None,
    images_dir: Path | None,
    expected_names: tuple[str, ...],
    detail_dir: Path,
) -> dict[str, object]:
    row: dict[str, object] = {column: "" for column in CSV_COLUMNS}
    row["student"] = archive_path.stem

    try:
        # Lane S: dataset lớp có 1-3 người/ảnh nên không ép một skeleton mỗi ảnh.
        audit = audit_coco_keypoints_archive(
            archive_path, expected_names, single_person_per_image=starter is None
        )
    except ValidationError as error:
        row["structure"] = "FAIL"
        row["note"] = str(error).replace(str(archive_path), archive_path.name)
        return row
    row["structure"] = "PASS"
    # cảnh báo chung "structural không chứng minh giải phẫu" in một lần ở đầu bảng, không lặp mỗi dòng
    specific = [str(w) for w in audit["warnings"] if not str(w).startswith("Structural PASS")]
    if specific:
        row["note"] = "; ".join(specific)

    if starter is None or gold_dir is None or images_dir is None:
        return row

    with tempfile.TemporaryDirectory() as workspace:
        work = Path(workspace)
        coco_json = extract_coco_json(archive_path, str(audit["annotation_json_member"]), work)
        labels_dir = work / "labels"
        converted = run_tool(starter, CONVERTER, ["--coco", str(coco_json), "--out", str(labels_dir)])
        if converted.returncode != 0:
            row["note"] = f"convert lỗi: {converted.stderr.strip().splitlines()[-1] if converted.stderr.strip() else 'không rõ'}"
            return row

        detail_path = detail_dir / f"{archive_path.stem}.json"
        evaluated = run_tool(starter, EVALUATOR, [
            "--pred", str(labels_dir),
            "--gold", str(gold_dir),
            "--images", str(images_dir),
            "--out", str(detail_path),
        ])
        if evaluated.returncode != 0 or not detail_path.is_file():
            row["note"] = f"chấm lỗi: {evaluated.stderr.strip().splitlines()[-1] if evaluated.stderr.strip() else 'không rõ'}"
            return row

    summary = json.loads(detail_path.read_text(encoding="utf-8"))["summary"]
    findings = summary.get("findings", {})
    row.update({
        "mean_oks": summary["mean_oks"],
        "oks50": summary["oks50"],
        "oks75": summary["oks75"],
        "level": level_of(summary["mean_oks"], summary["oks75"]),
        "matched_people": summary["matched_people"],
        "missing_people": summary["missing_people"],
        "extra_people": summary["extra_people"],
        **{name: findings.get(name, 0) for name in HEADLINE_FINDINGS},
    })
    return row


def write_markdown(rows: list[dict[str, object]], path: Path, scored: bool) -> None:
    columns = list(CSV_COLUMNS) if scored else ["student", "structure", "note"]
    lines = [
        "# Bảng chấm Day 4",
        "",
        f"{len(rows)} bài nộp. OKS và tên lỗi do `tools/evaluate_pose_annotations.py` của starter sinh ra.",
        "",
        "`structure = PASS` chỉ nói file đúng định dạng COCO-17; nó **không** chứng minh vị trí "
        "giải phẫu, trái/phải hay quyết định visibility là đúng.",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Chấm hàng loạt ZIP export COCO Keypoints.")
    parser.add_argument("--submissions", type=Path, required=True, help="thư mục chứa các file .zip")
    parser.add_argument("--starter", type=Path, help="checkout repo starter; bỏ qua thì chỉ kiểm cấu trúc")
    parser.add_argument("--lane", choices=("S", "C"), default="S", help="S = 20 ảnh starter, C = 10 ảnh cabin")
    parser.add_argument("--gold", type=Path, help="ghi đè $GOLD_RELEASE_DIR nếu không nằm ở vị trí thường gặp")
    parser.add_argument("--images", type=Path, help="ghi đè thư mục ảnh dùng để chấm")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs/grading", help="thư mục kết quả")
    args = parser.parse_args()

    if not args.submissions.is_dir():
        print(f"FAIL: không thấy thư mục bài nộp {args.submissions}", file=sys.stderr)
        return 1
    archives = sorted(args.submissions.glob("*.zip"))
    if not archives:
        print(f"FAIL: không có file .zip nào trong {args.submissions}", file=sys.stderr)
        return 1

    starter = args.starter.resolve() if args.starter else None
    gold_dir = images_dir = None
    expected_names = PILOT_IMAGE_NAMES

    if args.lane == "S":
        if starter is None:
            print("FAIL: Lane S cần --starter để lấy ảnh, gold và toolchain chấm", file=sys.stderr)
            return 1
        expected_names = starter_image_names(starter)
        if not expected_names:
            print(f"FAIL: không thấy ảnh train trong {starter}", file=sys.stderr)
            return 1
        gold_dir = (args.gold or (find_gold_dir(starter) or Path("/nonexistent"))).resolve()
        gold_labels = gold_dir / GOLD_MARKER
        if not gold_labels.is_dir():
            print(
                "FAIL: không thấy $GOLD_RELEASE_DIR trong checkout. Gold chỉ được mở sau khi "
                "cả lớp đã khoá nhãn; truyền --gold nếu nó nằm chỗ khác.",
                file=sys.stderr,
            )
            return 1
        gold_dir = gold_labels
        images_dir = (args.images or (starter / "dataset/images/train")).resolve()
    elif starter is not None:
        print("NOTE: Lane C không có gold để chấm OKS — chỉ kiểm cấu trúc.", file=sys.stderr)
        starter = None

    detail_dir = args.out / "detail"
    detail_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for archive_path in archives:
        row = grade_one(archive_path, starter, gold_dir, images_dir, expected_names, detail_dir)
        rows.append(row)
        print(f"{row['structure']:4}  {row['student']}  OKS={row['mean_oks'] or '-'}  {row['note']}")

    # xếp bài cần chú ý lên đầu: fail cấu trúc trước, rồi OKS thấp dần lên
    rows.sort(key=lambda row: (row["structure"] == "PASS", row["mean_oks"] if row["mean_oks"] != "" else -1))

    csv_path = args.out / "summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    md_path = args.out / "summary.md"
    write_markdown(rows, md_path, scored=args.lane == "S")

    failed = sum(1 for row in rows if row["structure"] == "FAIL")
    print(f"\n{len(rows)} bài · {failed} bài fail cấu trúc\n{csv_path}\n{md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
