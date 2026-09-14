#!/usr/bin/env python3
"""Audit a CVAT COCO Keypoints export or a complete Day 4 submission."""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from day4_utils import (  # noqa: E402
    ValidationError,
    audit_coco_keypoints_archive,
    validate_submission_directory,
    write_visibility_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--export", type=Path, help="CVAT COCO Keypoints ZIP")
    mode.add_argument("--submission-dir", type=Path, help="directory with the three deliverables")
    parser.add_argument("--write-report", type=Path, help="write VISIBILITY_REPORT.csv")
    args = parser.parse_args()

    try:
        if args.export:
            report = audit_coco_keypoints_archive(args.export)
            if args.write_report:
                write_visibility_report(report, args.write_report)
        else:
            if args.write_report:
                parser.error("--write-report chỉ dùng với --export")
            report = validate_submission_directory(args.submission_dir)
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("PASS structural audit; semantic review vẫn bắt buộc.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
