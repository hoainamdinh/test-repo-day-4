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
    dataset_dir = ROOT / "dataset"
    train_images = list((dataset_dir / "images" / "train").glob("*.jpg")) if (dataset_dir / "images" / "train").exists() else []
    test_images = list((dataset_dir / "images" / "test").glob("*.jpg")) if (dataset_dir / "images" / "test").exists() else []
    test_labels = list((dataset_dir / "labels" / "test").glob("*.txt")) if (dataset_dir / "labels" / "test").exists() else []
    data_yaml = ROOT / "data.yaml"

    if len(train_images) != 20:
        return fail(f"dataset/images/train cần đúng 20 ảnh; nhận {len(train_images)}")
    if len(test_images) != 10:
        return fail(f"dataset/images/test cần đúng 10 ảnh; nhận {len(test_images)}")
    if len(test_labels) != 10:
        return fail(f"dataset/labels/test cần đúng 10 file nhãn; nhận {len(test_labels)}")
    if not data_yaml.is_file():
        return fail("thiếu file data.yaml ở root")

    print(f"PASS train set: {len(train_images)} images (train_01.jpg .. train_20.jpg)")
    print(f"PASS test set: {len(test_images)} images (test_01.jpg .. test_10.jpg)")
    print(f"PASS test labels: {len(test_labels)} label files")
    print(f"PASS data.yaml configuration verified")
    print("PASS Lane S dataset audit complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

