"""Chuyển đổi file ZIP COCO Keypoints 1.0 export từ CVAT thành các file nhãn YOLO Pose TXT (dataset/labels/train/*.txt)."""

import argparse
import json
import sys
import zipfile
from pathlib import Path


def convert_coco_zip_to_yolo(coco_zip_path: Path | str, output_dir: Path | str) -> int:
    coco_zip_path = Path(coco_zip_path)
    output_dir = Path(output_dir)

    if not coco_zip_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file COCO ZIP: {coco_zip_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(coco_zip_path, "r") as archive:
        json_members = [
            m for m in archive.namelist() if m.endswith(".json") and not m.startswith("__MACOSX")
        ]
        if not json_members:
            raise ValueError("Không tìm thấy file JSON nào trong file ZIP COCO.")

        coco_data = json.loads(archive.read(json_members[0]).decode("utf-8"))

    images_by_id = {img["id"]: img for img in coco_data.get("images", [])}

    annos_by_image: dict[int, list[dict]] = {}
    for ann in coco_data.get("annotations", []):
        img_id = ann.get("image_id")
        if img_id in images_by_id:
            annos_by_image.setdefault(img_id, []).append(ann)

    converted_count = 0
    for img_id, img_info in images_by_id.items():
        fname = Path(img_info.get("file_name", "")).name
        stem = Path(fname).stem
        txt_path = output_dir / f"{stem}.txt"

        img_w = float(img_info.get("width", 1))
        img_h = float(img_info.get("height", 1))

        lines = []
        for ann in annos_by_image.get(img_id, []):
            bbox = ann.get("bbox", [])  # [x, y, w, h]
            if len(bbox) != 4:
                continue
            x, y, w, h = bbox
            cx = (x + w / 2.0) / img_w
            cy = (y + h / 2.0) / img_h
            nw = w / img_w
            nh = h / img_h

            kpts = ann.get("keypoints", [])  # [x1, y1, v1, x2, y2, v2, ...]
            kpt_parts = []
            for i in range(0, len(kpts), 3):
                if i + 2 < len(kpts):
                    kx, ky, kv = kpts[i], kpts[i + 1], kpts[i + 2]
                    nkx = (kx / img_w) if kv > 0 else 0.0
                    nky = (ky / img_h) if kv > 0 else 0.0
                    kpt_parts.extend([f"{nkx:.6f}", f"{nky:.6f}", str(int(kv))])

            line = f"0 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f} " + " ".join(kpt_parts)
            lines.append(line)

        txt_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        converted_count += 1

    print(f"[SUCCESS] Đã chuyển đổi {converted_count} file nhãn YOLO Pose vào: {output_dir.resolve()}")
    return converted_count


def main():
    parser = argparse.ArgumentParser(
        description="Chuyển đổi COCO Keypoints 1.0 ZIP sang nhãn YOLO Pose TXT"
    )
    parser.add_argument("--coco", type=Path, required=True, help="Đường dẫn tới file ZIP export từ CVAT")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("dataset/labels/train"),
        help="Thư mục xuất file nhãn TXT (mặc định: dataset/labels/train)",
    )
    args = parser.parse_args()

    try:
        convert_coco_zip_to_yolo(args.coco, args.out)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
