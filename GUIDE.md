# Hướng dẫn gán nhãn & thực thi Day 4 (Lane S)

Tài liệu này hướng dẫn quy trình gán nhãn COCO-17 và thực thi cho **Lane S**.

## 0. Luật chung
- `left_*` và `right_*` là bên trái/phải của **người trong ảnh**, không phải bên màn hình.
- **Mọi người trong ảnh đều đủ 17 điểm.** Điểm không dùng được thì gắn cờ, không xoá.
- `v=2` nhìn thấy; `v=1` bị che nhưng **còn trong khung** (bật `Occluded` - `q`); `v=0` **ra ngoài mép ảnh** (bật `Outside` - `o`).
- Không dùng `Hidden` (`h`).

## 1. Quy trình làm việc của Học viên

1. **Gắn nhãn trên CVAT**:
   - Gán 20 ảnh trong tập `dataset/images/train/` trên CVAT với skeleton `person` (17 keypoints).
   - Export dữ liệu dạng **COCO Keypoints 1.0** (file ZIP).

2. **Chuyển đổi nhãn tại local**:
   - Chuyển đổi file COCO ZIP thành 20 file nhãn YOLO Pose (`dataset/labels/train/*.txt`):
     ```bash
     python scripts/convert_coco_to_yolo.py --coco path/to/coco_export.zip --out dataset/labels/train
     ```
   - Commit & push 20 file nhãn `.txt` vừa sinh lên repository GitHub cá nhân.

3. **Chạy Colab fine-tune & Đánh giá**:
   - Mở Colab `notebooks/day4_pose_finetune_yolo26.ipynb`.
   - Nhập `REPO_URL` (Link repo GitHub) để clone code và nhãn của học viên.
   - Upload file `gold_labels.zip` (được cấp).
   - Chạy toàn bộ cell: Notebook sẽ tự động đánh giá nhãn học viên so với Gold set (`eval_vs_gold.json`), huấn luyện YOLO Pose, đánh giá mô hình (`eval_model.json`, `visibility_report.json`), và nén tải về máy local để làm `reports/REPORT.md`.

