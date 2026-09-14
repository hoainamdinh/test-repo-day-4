#!/usr/bin/env python3
"""Generate the Day 4 no-code Colab notebook from tested local helpers."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks" / "day4-pose-quality.ipynb"


def markdown(cell_id, source):
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(cell_id, source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


helper_source = (ROOT / "day4_utils.py").read_text(encoding="utf-8")
helper_source = helper_source.replace("from __future__ import annotations\n\n", "")

cells = [
    markdown(
        "title-and-boundary",
        """# Day 4 — Audit COCO-17 pose và đóng gói bài nộp

Core path không yêu cầu viết code. Chỉ mở notebook **sau independent attempt và self-QC** rồi chạy cell theo thứ tự.

Structural PASS không chứng minh keypoint đúng giải phẫu, left/right hoặc visibility decision. Model output và validator không phải ground truth.
""",
    ),
    code("embedded-tested-helpers", helper_source),
    code(
        "workspace-preflight",
        '''# 0 — Tạo workspace sạch; không cài package.
import json
import shutil
from pathlib import Path

WORK_DIR = Path("/content/day4_submission") if Path("/content").exists() else Path("day4_submission")
if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR)
WORK_DIR.mkdir(parents=True)
print(f"PASS preflight: {WORK_DIR}")
''',
    ),
    code(
        "upload-helper",
        '''# Helper upload: local có thể đặt file cạnh notebook; Colab dùng widget.
def upload_one(expected_name):
    for candidate in (Path("/content") / expected_name, Path(expected_name)):
        if candidate.is_file():
            print(f"Dùng file đã có: {candidate.resolve()}")
            return candidate.read_bytes()
    try:
        from google.colab import files
    except ImportError as error:
        raise RuntimeError(
            f"Đặt {expected_name} cạnh notebook hoặc chạy trong Colab."
        ) from error
    print(f"Chọn đúng file {expected_name}")
    uploaded = files.upload()
    if len(uploaded) != 1:
        raise ValidationError(f"Cần đúng một file; nhận {len(uploaded)}")
    name, payload = next(iter(uploaded.items()))
    if name != expected_name:
        raise ValidationError(f"Cần tên {expected_name}; nhận {name}")
    return payload
''',
    ),
    code(
        "audit-export",
        '''# 1 — Upload COCO export, audit và sinh visibility report.
export_path = WORK_DIR / "COCO_KEYPOINTS_EXPORT.zip"
export_path.write_bytes(upload_one("COCO_KEYPOINTS_EXPORT.zip"))
audit_report = audit_coco_keypoints_archive(export_path)
visibility_path = write_visibility_report(audit_report, WORK_DIR / "VISIBILITY_REPORT.csv")
print(json.dumps(audit_report, ensure_ascii=False, indent=2))
print(f"PASS structural audit; report: {visibility_path}")
try:
    from google.colab import files
    files.download(str(visibility_path))
except ImportError:
    print(f"Local output: {visibility_path.resolve()}")
''',
    ),
    markdown(
        "semantic-checkpoint",
        """## Checkpoint semantic

Chỉ tiếp tục khi bạn đã hoàn thành ba self-QC pass, peer review và rework trên CVAT. Copy `POSE_REVIEW_TEMPLATE.md`, điền evidence thật và đổi ba marker thành `yes`. Nếu annotation đổi, re-export rồi chạy lại từ cell 1.
""",
    ),
    code(
        "validate-review",
        '''# 2 — Upload POSE_REVIEW.md và kiểm ba-file contract.
review_path = WORK_DIR / "POSE_REVIEW.md"
review_path.write_bytes(upload_one("POSE_REVIEW.md"))
submission_report = validate_submission_directory(WORK_DIR)
print(json.dumps(submission_report, ensure_ascii=False, indent=2))
print("PASS three-file contract")
''',
    ),
    code(
        "package-submission",
        '''# 3 — Điền ba biến và tạo ZIP nộp bài.
KHOA = "KX"
HO_VA_TEN_KHONG_DAU = "HoVaTen"
MSSV = "MSSV"

if not re.fullmatch(r"K[0-9A-Za-z]+", KHOA):
    raise ValidationError("KHOA ví dụ K4")
if not re.fullmatch(r"[A-Za-z0-9]+", HO_VA_TEN_KHONG_DAU) or HO_VA_TEN_KHONG_DAU == "HoVaTen":
    raise ValidationError("Điền họ tên không dấu, không khoảng trắng")
if not re.fullmatch(r"[A-Za-z0-9]+", MSSV) or MSSV == "MSSV":
    raise ValidationError("Điền MSSV")

submission_name = f"{KHOA}-DAY04-{HO_VA_TEN_KHONG_DAU}-{MSSV}.zip"
submission_path, _ = package_submission(WORK_DIR, Path(submission_name))
print(f"PASS package: {submission_path}")
try:
    from google.colab import files
    files.download(str(submission_path))
except ImportError:
    print(f"Local output: {submission_path.resolve()}")
''',
    ),
    markdown(
        "final-check",
        """## Kiểm cuối

Giải nén ZIP vừa tạo. Root phải có đúng `COCO_KEYPOINTS_EXPORT.zip`, `VISIBILITY_REPORT.csv`, `POSE_REVIEW.md`. Nộp qua kênh riêng tư của lớp; không commit annotation hoặc submission vào repo public.
""",
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"name": "day4-pose-quality.ipynb", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(TARGET)
