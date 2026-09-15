# Day 4 pilot — Keypoint & Pose

> **Trạng thái: `pilot-v0.4-alpha — ready to execute gates`.** Chưa release, chưa freeze.
> Pilot này **không phải** repo phát cho người học. Repo lớp học là
> [Day4-TrackData-Keypoint-Pose](https://github.com/VinUni-AI20k/Day4-TrackData-Keypoint-Pose).
> Việc của pilot là chạy thử trọn route đó và bảo chứng phần privacy/self-hosted chưa được phủ.

Starter là **technical compatibility baseline** — nó định nghĩa schema, định dạng export, cách
tính OKS và bộ tool. Nó **không** giữ quyền quyết định lab: timeline, learning objective, rubric,
model và quyết định release đều thuộc owner của pilot. Đọc `STARTER_ALIGNMENT.md` mục 0 trước
mọi việc khác.

## Pilot làm gì

Pilot này tập trung kiểm chứng trọn vẹn **Lane S — starter route** cho buổi lab 240 phút:

- **Dữ liệu**: 20 ảnh train + 10 ảnh test của starter (29 người).
- **Task CVAT**: Hai task (A = 20 ảnh/`person`; B = 5 ảnh/`hand`+`face`).
- **Chấm**: OKS với protected gold release (`gold_labels.zip`).
- **Tài liệu**: `GUIDE.md` + `RUBRIC.md` của starter.

## Lane S — chạy đúng route của người học

Lịch dưới đây mirror 7 chặng của starter vì pilot đang **kiểm chứng** chính lịch đó. Nếu số đo
T-10 cho thấy 240 phút không đủ, đổi lịch là quyết định của owner — `STARTER_ALIGNMENT.md` mục 0.

| Phút | Chặng | Evidence/checkpoint |
| ---: | --- | --- |
| 0-20 | Dựng 3 skeleton label, tạo **task A** (20 ảnh, `person`) | A — 3 skeleton đúng tên/thứ tự, chế độ Shape |
| 20-40 | Warm-up 2 ảnh, export thử, soi bằng `visualize_pose.py` | B — export đúng **COCO Keypoints 1.0** |
| 40-130 | Gán 18 ảnh còn lại của task A + **task B** (5 ảnh, `hand`+`face`) | C — đủ 29 người/17 điểm ở task A; export riêng `annotations/face_hand/` |
| 130-150 | Ba lượt kiểm, visibility report, kiểm chéo, **khoá nhãn** | D — `check_pose_labels.py` 0 lỗi + `visibility_report.md` |
| 150-190 | Nhận gold (`gold_labels.zip`), chấm bằng OKS, rework | E — `outputs/eval_vs_gold.json` trước và sau rework |
| 190-230 | Colab: fine-tune, visualize, đánh giá | F — `outputs/eval_model.json` |
| 230-240 | Báo cáo, commit, push | đủ 9 deliverable |

Mốc 150 là mốc cứng: gold chỉ được phát qua file `gold_labels.zip` sau khi cả lớp đã khoá nhãn.

Task B là **task CVAT thứ hai**, không phải thêm label vào task A: topology 21+5 điểm không trộn
vào bộ 17 điểm, và bộ này không được chấm bằng OKS vì không có gold cho nó.

### Bộ nộp Lane S (9 mục, theo starter)

```text
dataset/labels/train/*.txt                                  nhãn YOLO Pose, 56 số/dòng
annotations/coco_keypoints/person_keypoints_default.json    export COCO Keypoints 1.0
annotations/face_hand/                                      21 điểm tay + 5 điểm mặt, 5 ảnh
reports/visibility_report.md + outputs/visibility_report.json
GUIDELINE_MINI.md
outputs/eval_vs_gold.json
outputs/eval_model.json
reports/REPORT.md
reports/review_partner.md
```

### Chạy Lane S

```bash
git clone https://github.com/VinUni-AI20k/Day4-TrackData-Keypoint-Pose ../tmp/day4-starter
git -C ../tmp/day4-starter checkout 79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3
python3 scripts/check-starter-alignment.py --starter ../tmp/day4-starter
```

Checker **fail** nếu HEAD của checkout khác commit đã pin `79f6724…`. Muốn khảo sát commit mới
thì thêm `--allow-unpinned`; nhận commit mới là quyết định của owner, kèm cập nhật pin trong
script và `STARTER_ALIGNMENT.md`.

Checker phải PASS trước khi chạy pilot. Sau đó làm theo `GUIDE.md` của starter, chặng 1 đến 7,
và ghi mọi quan sát vào `PILOT_RUN_SHEET.md`.

Bốn lỗi cần đo riêng vì pilot cũ chưa từng chạm tới: **nhầm người** (ảnh 2-3 người),
**đảo trái/phải**, **xoá khớp bị che**, và **export nhầm COCO 1.0 thay vì COCO Keypoints 1.0**.

## Model

Owner pilot đã khoá cấu hình pilot là `yolo26n-pose.pt`, đúng với notebook của starter; không
tự chuyển sang model khác khi checkpoint lỗi. Notebook cài `ultralytics` không pin version, nên
gate G-04 phải ghi chính xác version cài được trên Colab T4. Learning objective vẫn model-neutral.

## Release gate

Sáu gate trong `STARTER_ALIGNMENT.md` mục 6 — G-01 route đầy đủ, G-02 multi-person trên CVAT
Docker, G-03 đo bộ face/hand, G-04 Colab T4, G-05 lane separation (đã tự động), G-06 timed
dry-run 240 phút. Chỉ freeze `pilot-v0.4` khi cả sáu pass.

Cách chạy: `PILOT_TEST_RUNBOOK.md`. Ghi kết quả: `PILOT_RUN_SHEET.md`.
Trước khi đổi bất kỳ ảnh nào: `DATA_GOVERNANCE.md`.
