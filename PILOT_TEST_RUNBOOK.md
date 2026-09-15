# Pilot test runbook — Day 4

Mỗi T-ID dưới đây phục vụ đúng một gate trong `STARTER_ALIGNMENT.md` mục 6. Ghi kết quả vào
`PILOT_RUN_SHEET.md`. Ký hiệu đường dẫn (`$STARTER`, `$STARTER_ASSETS_DIR`, `$GOLD_RELEASE_DIR`)
định nghĩa ở `STARTER_ALIGNMENT.md` mục 1; `scripts/check-starter-alignment.py` in ra đường dẫn
thật của chúng.

Runbook này **chỉ sinh bằng chứng**. Không T-ID nào được tự đổi scope, tự cắt bộ face/hand hay
tự đổi cấu hình model: những quyết định đó thuộc owner pilot và phải được ghi vào bảng
"Decisions pending owner" trong `PILOT_RUN_SHEET.md` trước khi áp dụng.

| T-ID | Gate | Chặn freeze |
| --- | --- | --- |
| T-01 Repository contract | — | có |
| T-02 Alignment contract | G-05 | có |
| T-04 CVAT round-trip multi-person | G-02 | có |
| T-05 Starter toolchain round-trip | G-01 | có |
| T-06 Gold release drill | G-01 | có |
| T-07 Colab T4 | G-04 | có |
| T-08 Bộ face/hand | G-03 | có |
| T-10 Timed 240-minute dry-run | G-06 | có |
| T-11 Freeze | — | — |

## T-01 — Repository contract

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: toàn bộ test pass; notebook rebuild byte-for-byte giống nhau.

## T-02 — Lane separation (G-05)

```bash
git clone https://github.com/VinUni-AI20k/Day4-TrackData-Keypoint-Pose ../tmp/day4-starter
git -C ../tmp/day4-starter checkout 79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3
python3 scripts/check-starter-alignment.py --starter ../tmp/day4-starter
```

Expected: PASS mọi check. Fail nếu:

- HEAD của checkout **khác** commit đã pin `79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3`;
- hình dạng baseline đổi (số ảnh, `kpt_shape`, `flip_idx`, thứ tự keypoint, thiếu tool trong
  bộ 6 gồm `evaluate_pose_annotations.py`, evaluator mất một trong ba finding pilot dựa vào,
  evaluator không còn dùng OKS);
- thiếu `$STARTER_ASSETS_DIR`, thiếu một trong 3 skeleton label 17/21/5, hoặc thiếu một trong
  3 file skeleton SVG;
- có ảnh cabin trong `dataset/` của baseline, hoặc có gold/mapping nguồn lọt vào repo pilot.

Khảo sát một commit mới hơn thì chạy thêm `--allow-unpinned`. Kết quả đó **không** tự cập nhật
pin: nhận commit mới là quyết định của owner, kèm sửa `PINNED_STARTER_COMMIT` trong script,
`STARTER_ALIGNMENT.md` và `PILOT_RUN_SHEET.md`.



## T-04 — CVAT round-trip multi-person (G-02)

POC schema/export cũ: **pass** trên local Docker ngày 2026-09-14.
POC đó chỉ có một skeleton/ảnh, nên **không** phủ được phần dưới đây.

Cấu trúc bắt buộc: **một project, hai task** — task A (20 ảnh, `person`) và task B (5 ảnh,
`hand`+`face`, export riêng). Xem `CVAT_TASK_SPEC.md` mục "Lane S".

Chuẩn bị chung:

1. Ghi URL/version/build của CVAT classroom vào `PILOT_RUN_SHEET.md`.
2. Tạo project theo `CVAT_TASK_SPEC.md`: dán `labels_day4.json` từ `$STARTER_ASSETS_DIR` vào tab
   **Raw**, kiểm cả ba skeleton `person`/`hand`/`face` xuất hiện đúng số sublabel 17/21/5.
3. Lặp lại bằng đường upload ba file `.svg` trên một project khác — cả hai đường phải chạy được
   trên CVAT Docker (D-07). Xác nhận `From model → Human pose estimation` **không** khả dụng và
   ghi lại mã lỗi.

Task A — multi-person, phần chính của G-02:

4. Tạo task A, upload 20 ảnh `dataset/images/train` của baseline. Chỉ vẽ `person`.
5. Trên `train_13` (3 người) đặt đủ 3 skeleton `person`; trên các ảnh 2 người đặt đủ 2.
6. Save → reload → mỗi skeleton giữ đúng định danh; không có cạnh nối chéo giữa hai cơ thể.
7. Thử đổi thứ tự vẽ trên một ảnh 2 người rồi export lại; mapping người không được đổi.
8. Tạo ít nhất một point ở mỗi state Visible/Occluded/Outside, save/reload, export
   **COCO Keypoints 1.0**, kiểm mapping `v=2/1/0`. Đếm đúng 29 annotation trên 20 image record.

Task B — bộ face/hand, phần đo thời lượng của G-03 (chi tiết ở T-08):

9. Tạo **task CVAT thứ hai** trong cùng project với 5 ảnh chọn lại từ bộ 20. Không vẽ lại `person`.
10. Vẽ `hand` 21 điểm và `face` 5 điểm; save → reload → kiểm sublabel không đổi tên/thứ tự.
11. Export **riêng** và đặt vào `annotations/face_hand/`. Xác nhận export của task A không đổi và
    không chứa annotation `hand`/`face`.

Fail nếu tên/thứ tự sublabel đổi, `v` mapping sai, filename không giữ, số annotation/ảnh sai,
task B rò vào export của task A, hoặc UI guide không khớp. Sửa contract/guide và chạy lại;
không bảo sinh viên sửa JSON.

## T-05 — Starter toolchain round-trip (G-01)

Chạy trên chính export của **task A** ở T-04, trong thư mục `$STARTER`:

```bash
python3 tools/coco_kp_to_yolo_pose.py   # COCO Keypoints 1.0 -> dataset/labels/train/*.txt
python3 tools/check_pose_labels.py      # phải 0 lỗi định dạng
python3 tools/visibility_report.py      # reports/visibility_report.md + outputs/visibility_report.json
python3 tools/visualize_pose.py         # soi mắt thường vài ảnh
```

Expected: 20 file `.txt`, mỗi dòng 56 số, tổng 29 dòng. Cảnh báo `v=0` giữa khung là **thông tin**,
không phải lỗi — chính protected gold release cũng có 8 cảnh báo ở train và 4 ở test (D-08).

Kiểm luôn phần validator bắt lỗi: export lại cùng task ở định dạng **COCO 1.0** và xác nhận
converter/`check_pose_labels.py` từ chối nó. Đây là cổng "trần 40 điểm" trong thang điểm baseline
mà owner đang dùng làm điểm khởi đầu.

## T-06 — Gold release drill (G-01)

Diễn tập đúng mốc phút 150:

1. Khoá nhãn trước (commit/tag hoặc snapshot hash) — ghi hash vào run sheet.
2. Chỉ sau khi khoá mới mở **protected gold release** (`$GOLD_RELEASE_DIR`) và đọc tại chỗ. Gold
   **không** đi vào repo pilot và không vào repo learner (`REFERENCE_REVIEW_PROTOCOL.md`).
3. ```bash
   python3 tools/evaluate_pose_annotations.py   # outputs/eval_vs_gold.json
   ```
4. Đọc `findings`, sửa nhãn trên CVAT, export lại, chạy lại — lưu cả hai bản JSON.

Expected: đo được OKS trước/sau rework; ngưỡng baseline là mean ≥ 0.75, OKS@0.75 ≥ 0.70 và
0 lỗi `dao_trai_phai`. Nếu đường này không kịp trong 40 phút của chặng 5, đó là finding của G-06
— ghi lại, không tự đổi ngưỡng hay đổi lịch.

Đối chiếu: `make_mock_student.py --quality average` cho mean OKS `0.6921`, OKS@0.75 `0.5172`,
29/29 người khớp — dùng làm baseline khi nghi ngờ pipeline chấm sai.

## T-07 — Colab T4 (G-04)

Mở `$STARTER/notebooks/day4_pose_finetune_yolo26.ipynb` trên Colab, runtime **T4**:

T-07 **chỉ ghi bằng chứng**. Nó không chốt model và không đổi cấu hình train.

1. Ghi lại version `ultralytics` thực tế cài được (notebook `install -U`, không pin — D-05).
2. Cấu hình pilot đã khoá `MODEL_NAME = yolo26n-pose.pt`. Ghi checkpoint thực tế tải được. Nếu
   checkpoint này không lấy được, ghi lỗi nguyên văn và giữ G-04 là fail; không tự chuyển model.
3. Chạy đủ 80 epoch với `seed=20260915 fliplr=0.5`, sinh `outputs/eval_model.json`.
4. Ghi thời gian train thật. Nếu vượt 40 phút của chặng 6, ghi con số đó vào
   "Decisions pending owner" trong `PILOT_RUN_SHEET.md`; **không** tự giảm epoch.

Fail nếu không sinh được `eval_model.json`. `pose_mAP` thấp **không** phải fail — 20 ảnh là quá
ít, và thang điểm baseline đã nói rõ điểm model thấp không bị trừ.

## T-08 — Bộ face/hand, task B (G-03)

Chạy trên **task CVAT thứ hai** đã tạo ở T-04 bước 9-11: 5 ảnh, `hand` 21 điểm + `face` 5 điểm,
export riêng vào `annotations/face_hand/`. Bộ này không có gold và **không** chấm bằng OKS.

T-08 **chỉ sinh số đo**:

1. Bấm giờ từng ảnh, tách riêng thời gian dựng task B khỏi thời gian annotate.
2. Ghi tổng thời gian task B và tổng thời gian chặng 3 (18 ảnh còn lại của task A + task B).
3. Ghi số lần phải sửa lại do nhầm topology 21/5 với 17.
4. Ghi thời gian export riêng và kiểm export của task A không bị ảnh hưởng.

Kết quả đi vào `PILOT_RUN_SHEET.md` dưới dạng số. Cấu hình đã khoá task B là **core** trong 90
phút của chặng 3; T-08 chỉ cho biết cấu hình đó có hoàn thành được hay không. Không tự cắt bộ
face/hand — D-06, `STARTER_ALIGNMENT.md` mục 0.

## T-10 — Timed 240-minute dry-run (G-06, blocking)

Chạy **đúng route Lane S của starter**, 7 chặng:

- một learner mới/non-tech;
- một learner có kinh nghiệm;
- cùng schema, evidence và thang điểm đang dùng, gồm cả task A và task B;
- ghi checkpoint A–F theo bảng lịch trong `README.md`, số lần hỗ trợ, rework và thời gian hoàn tất;
- ghi riêng thời điểm khoá nhãn — nếu trễ hơn phút 150 thì chặng gold bị ép.

Fail nếu novice không đạt đủ 9 deliverable trước phút 240.

Khi fail, T-10 **chỉ ghi lại** chặng nào vượt giờ và vượt bao nhiêu. Runbook **không** có
fallback tự động: task B vẫn core, train vẫn 80 epoch và tổng thời lượng vẫn 240 phút. Bất kỳ
đổi scope nào sau pilot phải được owner ghi thành một quyết định mới rồi chạy lại T-10; số đo cũ
không còn giá trị cho cấu hình mới.

## T-11 — Freeze

Trạng thái hiện tại là `pilot-v0.4-alpha — ready to execute gates`. Chỉ freeze khi các chặng independent attempt và đánh giá sau self-QC hoàn tất. Freeze là **quyết định của owner**, chỉ được đặt lên bàn sau khi T-01 đến T-10 pass và version `ultralytics==8.4.145` được xác nhận.

Mọi thay đổi learning objective, schema, order, evidence, privacy boundary hoặc 240 phút đều phải quay lại vòng pilot và kiểm thử tương ứng. Baseline đổi dataset hay tool thì chạy lại T-02 trước tiên.

