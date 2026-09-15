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

| | Lane S — starter route | Lane C — cabin compatibility drill |
| --- | --- | --- |
| Câu hỏi cần trả lời | người học có đi hết 7 chặng trong 240 phút không | schema/privacy có sống sót trên CVAT self-hosted và ảnh có mask không |
| Dữ liệu | 20 ảnh train + 10 ảnh test của starter (29 người) | 10 ảnh trong `data/images/` của pilot (10 người) |
| Task CVAT | **hai task**: A = 20 ảnh/`person`; B = 5 ảnh/`hand`+`face` | một task, chỉ `person` |
| Chấm | OKS với protected gold release | validator cấu trúc của pilot |
| Tài liệu | `GUIDE.md` + `RUBRIC.md` của **starter** | `GUIDE.md`, `RUBRIC.md` của pilot |

Không trộn hai lane. Ảnh cabin không vào `dataset/` của starter; nhãn cabin không dùng để
fine-tune; gold và mapping nguồn của starter không được sao vào pilot.

## Lane S — chạy đúng route của người học

Lịch dưới đây mirror 7 chặng của starter vì pilot đang **kiểm chứng** chính lịch đó. Nếu số đo
T-10 cho thấy 240 phút không đủ, đổi lịch là quyết định của owner — `STARTER_ALIGNMENT.md` mục 0.

| Phút | Chặng | Evidence/checkpoint |
| ---: | --- | --- |
| 0-20 | Dựng 3 skeleton label, tạo **task A** (20 ảnh, `person`) | A — 3 skeleton đúng tên/thứ tự, chế độ Shape |
| 20-40 | Warm-up 2 ảnh, export thử, soi bằng `visualize_pose.py` | B — export đúng **COCO Keypoints 1.0** |
| 40-130 | Gán 18 ảnh còn lại của task A + **task B** (5 ảnh, `hand`+`face`) + **khối cabin Lane C** (10 ảnh, ~60 phút) | C — đủ 29 người/17 điểm ở task A; export riêng `annotations/face_hand/`; bộ nộp Lane C |
| 130-150 | Ba lượt kiểm, visibility report, kiểm chéo, **khoá nhãn** | D — `check_pose_labels.py` 0 lỗi + `visibility_report.md` |
| 150-190 | Nhận gold, chấm bằng OKS, rework | E — `outputs/eval_vs_gold.json` trước và sau rework |
| 190-230 | Colab: fine-tune, visualize, đánh giá | F — `outputs/eval_model.json` |
| 230-240 | Báo cáo, commit, push | đủ 9 deliverable |

Mốc 150 là mốc cứng: gold chỉ được phát sau khi cả lớp đã khoá nhãn.

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

### Chấm cả lớp trong một lệnh

Bài nộp là ZIP export COCO Keypoints 1.0 của CVAT — đúng thứ CVAT xuất ra, người học không phải
convert tay. Chấm từng bài thì phải giải nén → convert sang YOLO → gọi evaluator, nên có script
làm trọn chuỗi đó cho cả thư mục bài nộp:

```bash
python3 scripts/grade-batch.py --submissions ~/baithu --starter ../tmp/day4-starter
```

Ra `outputs/grading/summary.csv` + `summary.md` (mỗi bài một dòng: pass/fail cấu trúc, mean OKS,
OKS@0.50/0.75, mức theo thang ba bậc, số người khớp/thiếu/thừa, đếm bốn lỗi trọng tâm) và JSON
chi tiết từng bài trong `outputs/grading/detail/`. Bài fail cấu trúc xếp lên đầu bảng.

Script **gọi `tools/*.py` của starter tại chỗ**, không fork — OKS và tên lỗi chỉ có một định
nghĩa. Nó cần `$GOLD_RELEASE_DIR`, nên chỉ chạy được sau khi cả lớp đã khoá nhãn. `outputs/` nằm
trong `.gitignore`, số liệu chấm không lọt vào git.

Lane C không có gold nên `--lane C` chỉ kiểm được cấu trúc, không ra OKS.

## Lane C — cabin compatibility drill

Pack 10 ảnh trong `data/images/` gồm 10 người từ ba nguồn công khai, hai lane bằng chứng:
2 crop calibration full-body (HSRD-100, CC BY 4.0) và 8 frame cabin (Driver Risk Behavior
Dataset CC BY 4.0, HADRIAN CC BY-NC 4.0). Không có ảnh AI. Pack chỉ dùng cho lớp học/phi
thương mại theo ràng buộc nghiêm nhất trong ba nguồn.

Drill này trả lời một câu hỏi mà dataset COCO của starter không trả lời được: khi khuôn mặt
bị mask, người gán nhãn xử lý 5 điểm mặt thế nào, và schema có chịu được không.

**Điểm lệch có chủ ý (D-01):** trên 8 ảnh cabin, `nose`/`left_eye`/`right_eye`/`left_ear`/
`right_ear` bắt buộc `Outside` (`v=0`) vì mask đã xoá evidence. Luật của starter ngược lại —
bị che mà còn trong khung thì `v=1` và vẫn đặt chấm. Vì vậy nhãn cabin **không tương thích**
với tập train của starter và không bao giờ được trộn vào đó.

```bash
python3 scripts/audit-data-pack.py
# tạo task CVAT theo CVAT_TASK_SPEC.md mục "Lane C", annotate theo GUIDE.md
python3 scripts/validate-submission.py --export COCO_KEYPOINTS_EXPORT.zip --write-report VISIBILITY_REPORT.csv
python3 scripts/validate-submission.py --submission-dir submission
```

Bộ nộp Lane C vẫn là ba file: `COCO_KEYPOINTS_EXPORT.zip`, `VISIBILITY_REPORT.csv`,
`POSE_REVIEW.md`. Validator chỉ chứng minh cấu trúc, schema, image mapping và consistency của
visibility count — không chứng minh keypoint đúng giải phẫu.

`lab-guide.html` là **hướng dẫn học viên của Lane C** — bản trực quan của khối cabin ~60 phút,
dùng được cho mọi mức kinh nghiệm: có on-ramp cho học viên nontech (cách mở CVAT, lệnh sao chép
được, bảng thuật ngữ), preflight checklist, sáu thao tác kèm ảnh chụp CVAT thật và lightbox xem
ảnh ngay trong trang. `GUIDE.md` của pilot là bản chữ tương đương. Nó chỉ phủ **khối cabin**,
nằm trong chặng gán nhãn (phút 40-130) của buổi lab 240 phút; learner guide cho phần còn lại của
route là `GUIDE.md` của starter và lịch 7 chặng ở mục "Lane S" bên trên.

## Model

Owner pilot đã khoá cấu hình pilot là `yolo26n-pose.pt`, đúng với notebook của starter; không
tự chuyển sang model khác khi checkpoint lỗi. Notebook cài `ultralytics` không pin version, nên
gate G-04 phải ghi chính xác version cài được trên Colab T4. POC Lane C lịch sử dùng
`yolo11n-pose.pt` với `ultralytics==8.4.145` trên macOS — xem `MODEL_DIAGNOSTIC_POC.md`; nó
không thay thế route người học. Learning objective vẫn model-neutral.

Trong Lane C, model chỉ là diagnostic tùy chọn sau self-QC, không phải ground truth, không tự
ghi đè annotation và không nằm trong rubric core.

## Release gate

Sáu gate trong `STARTER_ALIGNMENT.md` mục 6 — G-01 route đầy đủ, G-02 multi-person trên CVAT
Docker, G-03 đo bộ face/hand, G-04 Colab T4, G-05 lane separation (đã tự động), G-06 timed
dry-run 240 phút. Chỉ freeze `pilot-v0.4` khi cả sáu pass.

Cách chạy: `PILOT_TEST_RUNBOOK.md`. Ghi kết quả: `PILOT_RUN_SHEET.md`.
Trước khi đổi bất kỳ ảnh nào: `DATA_GOVERNANCE.md`.
