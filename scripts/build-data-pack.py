#!/usr/bin/env python3
"""Build the 10-person, two-lane Day 4 pack without generative AI."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

import certifi
from PIL import Image, ImageDraw, ImageEnhance


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "data" / "source-selection.json"
IMAGE_DIR = ROOT / "data" / "images"
MANIFEST = ROOT / "data" / "image-manifest.csv"

MANIFEST_COLUMNS = (
    "image_id",
    "filename",
    "role",
    "evidence_lane",
    "participant_code",
    "setup_id",
    "width",
    "height",
    "sha256",
    "source_type",
    "source_dataset",
    "source_version",
    "source_doi",
    "source_page",
    "source_file",
    "source_locator",
    "source_frame_sha256",
    "source_integrity_reference",
    "source_behavior_hint",
    "transform",
    "teaching_stressor",
    "distribution_status",
    "privacy_review",
    "facial_keypoints_scored",
    "face_evidence",
    "full_body_evidence",
    "license_basis",
    "license_url",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "VinUni-Day4-Lab-Pack/0.2"})
    tls_context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=120, context=tls_context) as response, path.open(
        "wb"
    ) as target:
        shutil.copyfileobj(response, target, length=1024 * 1024)


def validate_box(box: list[int], size: tuple[int, int], field: str) -> tuple[int, int, int, int]:
    if len(box) != 4:
        raise ValueError(f"{field} must contain x1, y1, x2, y2")
    x1, y1, x2, y2 = box
    width, height = size
    if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
        raise ValueError(f"{field} is outside {width}x{height}: {box}")
    return x1, y1, x2, y2


def crop_driver(image: Image.Image, box: list[int] | None) -> Image.Image:
    if box is None:
        return image
    return image.crop(validate_box(box, image.size, "crop_box"))


def redact_faces(image: Image.Image, boxes: list[list[int]]) -> Image.Image:
    """Apply opaque face masks; this is privacy reduction, not anonymisation."""

    result = image.copy()
    drawer = ImageDraw.Draw(result)
    radius = max(8, round(min(result.size) * 0.015))
    for index, box in enumerate(boxes):
        drawer.rounded_rectangle(
            validate_box(box, result.size, f"face_boxes[{index}]"),
            radius=radius,
            fill=(74, 79, 86),
        )
    return result


def apply_transform(image: Image.Image, transform: str) -> Image.Image:
    if transform == "baseline":
        return image
    if transform == "glare":
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        width, height = image.size
        ImageDraw.Draw(overlay).polygon(
            [(0, 0), (round(width * 0.52), 0), (round(width * 0.30), height), (0, height)],
            fill=(255, 248, 228, 112),
        )
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    if transform == "low-light":
        return ImageEnhance.Contrast(ImageEnhance.Brightness(image).enhance(0.42)).enhance(1.16)
    if transform == "partial-obstruction":
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        width, height = image.size
        ImageDraw.Draw(overlay).ellipse(
            (-round(width * 0.16), round(height * 0.46), round(width * 0.32), round(height * 1.12)),
            fill=(18, 22, 27, 218),
        )
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    if transform == "compression":
        return image
    raise ValueError(f"Unknown transform: {transform}")


def cached_hadrian_name(item: dict[str, object]) -> str:
    participant = str(item["participant_code"]).split("-", maxsplit=1)[1]
    return f"id-{participant}-t{int(item['timestamp_seconds']):05d}.jpg"


def extract_hadrian_frame(item: dict[str, object], output: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to retrieve HADRIAN frames")
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(item["timestamp_seconds"]),
        "-i",
        str(item["source_url"]),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        "-map_metadata",
        "-1",
        "-y",
        str(output),
    ]
    last_error = ""
    for attempt in range(1, 4):
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and output.is_file() and output.stat().st_size > 0:
            return
        last_error = result.stderr.strip()
        output.unlink(missing_ok=True)
        time.sleep(attempt)
    raise RuntimeError(f"Unable to extract {item['source_filename']}: {last_error}")


def load_mendeley_image(archive: zipfile.ZipFile, item: dict[str, object]) -> Image.Image:
    member = str(item["source_member"])
    payload = archive.read(member)
    actual_hash = sha256_bytes(payload)
    if actual_hash != item["source_frame_sha256"]:
        raise ValueError(f"Source member hash mismatch for {member}: {actual_hash}")
    with Image.open(io.BytesIO(payload)) as source:
        return source.convert("RGB")


def load_hadrian_image(
    item: dict[str, object], temporary_dir: Path, cached_frame_dir: Path | None
) -> Image.Image:
    raw = temporary_dir / cached_hadrian_name(item)
    cached = cached_frame_dir / raw.name if cached_frame_dir else None
    if cached and cached.is_file():
        shutil.copyfile(cached, raw)
    else:
        extract_hadrian_frame(item, raw)
    actual_hash = sha256_file(raw)
    if actual_hash != item["source_frame_sha256"]:
        raise ValueError(f"Extracted frame hash mismatch for {raw.name}: {actual_hash}")
    with Image.open(raw) as source:
        return source.convert("RGB")


def load_hsrd_image(
    item: dict[str, object], temporary_dir: Path, cached_preview_dir: Path | None
) -> Image.Image:
    filename = str(item["source_filename"])
    raw = temporary_dir / filename
    cached = cached_preview_dir / filename if cached_preview_dir else None
    if cached and cached.is_file():
        shutil.copyfile(cached, raw)
    else:
        download(str(item["source_url"]), raw)
    actual_hash = sha256_file(raw)
    if actual_hash != item["source_frame_sha256"]:
        raise ValueError(f"HSRD preview hash mismatch for {filename}: {actual_hash}")
    with Image.open(raw) as source:
        return source.convert("RGB")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mendeley-archive",
        type=Path,
        help="Use a cached source ZIP after verifying its published SHA-256.",
    )
    parser.add_argument(
        "--hadrian-frame-dir",
        type=Path,
        help="Use cached ffmpeg frame extracts whose hashes match source-selection.json.",
    )
    parser.add_argument(
        "--hsrd-preview-dir",
        type=Path,
        help="Use cached HSRD-100 preview files whose hashes match source-selection.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    items = selection["images"]
    participants = [item["participant_code"] for item in items]
    if len(items) != 10 or len(set(participants)) != 10:
        raise ValueError("Pack must contain exactly 10 distinct participant codes")

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    expected_outputs = {item["output_filename"] for item in items}
    unexpected = sorted(
        path.name for path in IMAGE_DIR.iterdir() if path.is_file() and path.name not in expected_outputs
    )
    if unexpected:
        raise ValueError(f"Unexpected active images: {unexpected}")

    sources = selection["sources"]
    mendeley = sources["mendeley-risk-behavior"]
    with tempfile.TemporaryDirectory(prefix="day4-mixed-source-") as temporary:
        temporary_dir = Path(temporary)
        archive_path = args.mendeley_archive or temporary_dir / "mendeley-source.zip"
        if args.mendeley_archive is None:
            download(mendeley["archive_url"], archive_path)
        actual_archive_hash = sha256_file(archive_path)
        if actual_archive_hash != mendeley["archive_sha256"]:
            raise ValueError(f"Mendeley archive hash mismatch: {actual_archive_hash}")

        rows: list[dict[str, object]] = []
        with zipfile.ZipFile(archive_path) as archive:
            for item in items:
                source = sources[item["source_key"]]
                if item["source_key"] == "mendeley-risk-behavior":
                    image = load_mendeley_image(archive, item)
                    source_file = item["source_member"]
                    source_locator = f"archive-member:{item['source_member']}"
                    integrity_reference = f"archive-sha256:{mendeley['archive_sha256']}"
                    privacy_review = "local-opaque-mask-not-anonymous"
                elif item["source_key"] == "hadrian":
                    image = load_hadrian_image(item, temporary_dir, args.hadrian_frame_dir)
                    source_file = item["source_filename"]
                    source_locator = f"figshare-file:{item['source_file_id']}@{item['timestamp_seconds']}s"
                    integrity_reference = (
                        f"published-md5:{item['source_file_md5']};size:{item['source_file_size']}"
                    )
                    privacy_review = "source-mask-preserved-not-anonymous"
                    source_type = "public-real-derived"
                else:
                    image = load_hsrd_image(item, temporary_dir, args.hsrd_preview_dir)
                    source_file = item["source_filename"]
                    source_locator = f"huggingface-revision:{source['revision']}/{source_file}"
                    integrity_reference = f"lfs-sha256:{item['source_frame_sha256']}"
                    privacy_review = "consented-scan-render-identifiers-removed-not-anonymous"
                    source_type = "public-consented-scan-derived"

                if item["source_key"] == "mendeley-risk-behavior":
                    source_type = "public-real-derived"

                image = crop_driver(image, item.get("crop_box"))
                image = redact_faces(image, item.get("face_boxes", []))
                image = apply_transform(image, item["transform"])
                # Reconstruct from pixels so source JPEG comments/ICC/XMP cannot leak.
                image = Image.frombytes("RGB", image.size, image.convert("RGB").tobytes())

                output = IMAGE_DIR / item["output_filename"]
                quality = 38 if item["transform"] == "compression" else 90
                image.save(
                    output,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    progressive=False,
                    exif=b"",
                )
                width, height = image.size
                rows.append(
                    {
                        "image_id": item["image_id"],
                        "filename": item["output_filename"],
                        "role": item["role"],
                        "evidence_lane": item["evidence_lane"],
                        "participant_code": item["participant_code"],
                        "setup_id": item["setup_id"],
                        "width": width,
                        "height": height,
                        "sha256": sha256_file(output),
                        "source_type": source_type,
                        "source_dataset": source["dataset"],
                        "source_version": source["version"],
                        "source_doi": source.get("doi", ""),
                        "source_page": source["url"],
                        "source_file": source_file,
                        "source_locator": source_locator,
                        "source_frame_sha256": item["source_frame_sha256"],
                        "source_integrity_reference": integrity_reference,
                        "source_behavior_hint": item["source_behavior_hint"],
                        "transform": item["transform"],
                        "teaching_stressor": item["teaching_stressor"],
                        "distribution_status": "classroom-noncommercial",
                        "privacy_review": privacy_review,
                        "facial_keypoints_scored": "yes" if item["facial_keypoints_scored"] else "no",
                        "face_evidence": item["face_evidence"],
                        "full_body_evidence": item["full_body_evidence"],
                        "license_basis": source["license"],
                        "license_url": source["license_url"],
                    }
                )

    with MANIFEST.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Built {len(rows)} images from {len(sources)} sources / {len(participants)} participants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
