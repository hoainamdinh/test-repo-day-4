#!/usr/bin/env python3
"""Run the optional YOLO11n-pose comparison after human self-QC."""

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PINNED_ULTRALYTICS_VERSION = "8.4.145"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acknowledge-license-review", action="store_true")
    parser.add_argument("--model", default="yolo11n-pose.pt")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "yolo11-diagnostic")
    args = parser.parse_args()
    if not args.acknowledge_license_review:
        parser.error("Đọc THIRD_PARTY_NOTICES.md rồi truyền --acknowledge-license-review")

    try:
        import ultralytics
        from ultralytics import YOLO
    except ImportError:
        print(
            f"Cài optional dependency trước: python3 -m pip install ultralytics=={PINNED_ULTRALYTICS_VERSION}",
            file=sys.stderr,
        )
        return 2
    if ultralytics.__version__ != PINNED_ULTRALYTICS_VERSION:
        print(
            f"FAIL: cần ultralytics=={PINNED_ULTRALYTICS_VERSION}, nhận {ultralytics.__version__}",
            file=sys.stderr,
        )
        return 2

    args.output.mkdir(parents=True, exist_ok=True)
    model = YOLO(args.model)
    for image_path in sorted((ROOT / "data" / "images").glob("*.png")):
        model.predict(
            source=str(image_path),
            save=True,
            project=str(args.output.parent),
            name=args.output.name,
            exist_ok=True,
            verbose=False,
        )
        print(f"DIAGNOSTIC {image_path.name}")
    print(f"Output: {args.output}")
    print("Không dùng output này làm ground truth hoặc ghi đè CVAT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
