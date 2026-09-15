# Day 4 pilot run sheet

Trạng thái repo: **`pilot-v0.4-alpha — ready to execute gates`**.

Bảng bằng chứng cho từng gate trong `STARTER_ALIGNMENT.md` mục 6. Cách chạy: `PILOT_TEST_RUNBOOK.md`.
Ký hiệu đường dẫn (`$STARTER`, `$STARTER_ASSETS_DIR`, `$GOLD_RELEASE_DIR`, `$PROTECTED_SOURCE_DIR`)
định nghĩa ở `STARTER_ALIGNMENT.md` mục 1.

## Run metadata

- Date/time: 2026-09-14 (local technical POC) · 2026-09-15 (starter alignment check and CVAT two-task setup)
- Pilot operator: technical setup recorded; semantic annotation and timed participant runs pending
- CVAT URL/version/build: local Docker `http://localhost:8080`, CVAT v2.74.1
- Browser/OS: Codex in-app browser / macOS
- Starter commit đã đối chiếu: `79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3` (2026-09-15)
- Schema JSON SHA-256: `db7e27f8e716bf3f1724aeb325a57ce876347b598ea6df00cb1548dfd76a950a`
- Skeleton SVG SHA-256: `7c67a45fe59d16a1f4adcff791e9279d6be6f884c05b91017da168c8669b64df`

## Tổng trạng thái gate

| Gate | T-ID | Trạng thái | Bằng chứng |
| --- | --- | --- | --- |
| G-01 route đầy đủ | T-05, T-06 | pending | — |
| G-02 multi-person trên CVAT Docker | T-04 | in progress | Project/task setup verified; semantic multi-person round-trip remains pending |
| G-03 bộ face/hand | T-08 | pending | — |
| G-04 Colab T4 | T-07 | in progress | Tesla T4 and `ultralytics 8.4.152` verified; complete post-label train evidence remains pending |
| G-05 lane separation | T-02 | **pass** | `check-starter-alignment.py` 2026-09-15, toàn PASS + 3 NOTE |
| G-06 timed dry-run 240 phút | T-10 | pending | — |

## T-02 — Lane separation và alignment (G-05)

| Check | Kết quả | Ghi chú |
| --- | --- | --- |
| 20 ảnh train / 10 ảnh test | pass | |
| `dataset/labels/train` trống khi pull | pass | bản phát cho người học |
| 10 file nhãn test, 56 số/dòng | pass | 13 người |
| `kpt_shape: [17, 3]`, `flip_idx`, `val: dataset/images/test` | pass | |
| HEAD của checkout == commit đã pin `79f6724…` | pass | fail-closed; bỏ qua bằng `--allow-unpinned` |
| 6 tool chấm có mặt (gồm `evaluate_pose_annotations.py`) | pass | |
| Evaluator còn đủ 3 finding pilot dựa vào | pass | `dao_trai_phai`, `nham_nguoi`, `xoa_khop_bi_che` |
| Evaluator vẫn dùng OKS | pass | |
| Thấy `$STARTER_ASSETS_DIR` (chứa `labels_day4.json`) | pass | tìm theo hình dạng thư mục |
| Đủ 3 skeleton label 17/21/5 | pass | task A `person`; task B `hand`+`face` |
| Thứ tự 17 sublabel `person` trùng schema pilot | pass | |
| Đủ 3 skeleton SVG cho Configurator | pass | |
| 17 tên + 19 cạnh của baseline trùng schema pilot | pass | baseline 0-indexed, pilot 1-indexed |
| Không có ảnh cabin trong `dataset/` của baseline | pass | |
| Không có gold/mapping nguồn trong pilot | pass | |
| NOTE | — | checkout đang dùng có `$GOLD_RELEASE_DIR`; `MODEL_NAME = yolo26n-pose.pt`; `ultralytics` không pin |

## Đối chiếu toolchain starter (baseline, 2026-09-15)

| Kiểm | Kết quả |
| --- | --- |
| `check_pose_labels.py` trên `$GOLD_RELEASE_DIR/labels/train` | ĐẠT định dạng, 8 cảnh báo `v=0` giữa khung |
| `check_pose_labels.py` trên `dataset/labels/test` | ĐẠT định dạng, 4 cảnh báo |
| `make_mock_student.py --quality average` → `evaluate_pose_annotations.py` | 29/29 người khớp, mean OKS `0.6921`, OKS@0.50 `0.8621`, OKS@0.75 `0.5172` |
| Findings bài `average` | `dao_trai_phai` 4, `nham_nguoi` 2, `xoa_khop_bi_che` 17, `gold_khong_gan_nhan` 8 |

Ba con số OKS khớp bảng ba mức chất lượng mà baseline công bố.

## T-04 — CVAT round-trip (G-02)

Technical POC cũ, một skeleton/ảnh — vẫn hợp lệ cho phần schema/visibility:

| Check | Evidence path/hash | Result | Notes |
| --- | --- | --- | --- |
| SVG import and 17 ordered sublabels | task #14/job #10 | pass | importer contract includes labels-specification `<desc>` |
| Save/reload skeleton | task #14/job #10 | pass | 2 parent skeletons + 34 element shapes persisted |
| Visible → `v=2` | `VISIBILITY_REPORT.csv` | pass | visible counts present for all keypoints |
| Occluded → `v=1` | right_wrist row | pass | one occluded right wrist |
| Outside → `v=0` | ankle rows | pass | one outside value for each ankle |
| COCO Keypoints export audit | ZIP SHA `15b35b...fdbe` | pass | unedited CVAT export; 2 images/2 annotations |
| Visibility CSV reconciliation | CSV SHA `373ae7...8d5e` | pass | expected counts match UI states |
| Re-import when required | — | not applicable | learner submission path does not import |

Phần project + hai task — **chưa chạy**:

| Check | Task | Result | Notes |
| --- | --- | --- | --- |
| `labels_day4.json` dán tab Raw tạo đủ 3 skeleton (17/21/5) | project #5 | pass | `person`, `hand`, `face` were present in the project label configuration (2026-09-15) |
| Upload 3 file `.svg` tạo đủ 3 skeleton | project | pending | |
| `From model → Human pose estimation` không khả dụng trên Docker | project | pending | ghi lại mã lỗi (`/api/lambda/functions` 503) |
| Task A tạo được với 20 ảnh, chỉ dùng `person` | A, task #20 / job #18 | pass (setup) | importer completed 20 frames; `train_13.jpg` (frame 12) was opened and confirmed as a three-person image; no annotation was fabricated |
| `train_13` giữ đúng 3 skeleton qua save/reload | A | pending | |
| 7 ảnh 2 người giữ đúng 2 annotation khi export | A | pending | |
| Đổi thứ tự vẽ không đổi mapping người | A | pending | |
| Export task A: 20 image record / 29 annotation / 51 số | A | pending | |
| Task B tạo được như **task CVAT thứ hai** cùng project, 5 ảnh | B, task #21 / job #19 | pass (setup) | importer completed 5 frames; task page confirms frame range 0–4. The initial five files are a technical setup only, not the T-08 suitability/time trial |
| Task B chỉ có `hand` 21 + `face` 5, không vẽ lại `person` | B | pending | |
| Export riêng của task B vào `annotations/face_hand/` | B | pending | không chấm OKS |
| Export task A không chứa annotation `hand`/`face` | A+B | pending | kiểm rò rỉ giữa hai task |

Technical setup note (2026-09-15): CVAT form retries left one additional same-name project. It is not
used by the evidence above and has not been removed; manual cleanup remains pending. This does not
substitute for the required save/reload/export checks.

Live interaction finding (2026-09-15): in CVAT v2.74.1, choosing `Draw new skeleton → Shape`
creates the 17-point skeleton stack from one canvas click; the individual points then require
visual repositioning and QC. A coordinate-drag experiment produced invalid geometry and was undone
before saving. Task A therefore remains clean (0 saved annotations) and cannot be used as semantic
or export evidence until a human annotates the required people. This is a POC finding, not a
learner error or a change to the schema.

## v0.3 local Docker smoke

| Check | Evidence | Result | Notes |
| --- | --- | --- | --- |
| Final task creation | task #16/job #12 | pass | local Docker CVAT v2.74.1; 10 frames, range 0-9 |
| `person` skeleton import | task #16 | pass | edit view shows all 17 ordered COCO sublabels |
| Save/reload visibility semantics | — | pending | annotate representative calibration frames before freeze |
| COCO export/validator round-trip | — | pending | required before `pilot-v0.4` release decision |

## T-05/T-06 — Starter toolchain và gold drill (G-01)

| Check | Result | Notes |
| --- | --- | --- |
| `coco_kp_to_yolo_pose.py` trên export thật của pilot | pending | kỳ vọng 20 file, 29 dòng, 56 số/dòng |
| `check_pose_labels.py` 0 lỗi định dạng | pending | cảnh báo `v=0` là thông tin (D-08) |
| `visibility_report.py` sinh `.md` + `.json` | pending | |
| Export nhầm **COCO 1.0** bị toolchain từ chối | pending | cổng "trần 40 điểm" |
| Khoá nhãn trước rồi mới nhận gold | pending | ghi hash snapshot |
| `eval_vs_gold.json` trước rework | pending | mean OKS / OKS@0.75 |
| `eval_vs_gold.json` sau rework | pending | cổng ≥ 0.75 / ≥ 0.70 / 0 `dao_trai_phai` |

## T-07 — Colab T4 (G-04)

| Mục | Giá trị |
| --- | --- |
| Runtime | Tesla T4 · Google Compute Engine GPU runtime (2026-09-15) |
| `ultralytics` version thực tế | `8.4.152` |
| `torch` / CUDA | `2.11.0+cu128` · `torch.cuda.is_available() == True` |
| Setup notebook | `%pip -q install -U ultralytics` completed; the full setup cell elapsed 9 seconds before the data precondition stopped it |
| `MODEL_NAME` tải được | pending (`yolo26n-pose.pt`, cấu hình đã khoá) |
| Thời gian train 80 epoch | pending |
| `outputs/eval_model.json` sinh ra | pending |

Preflight 2026-09-15: the pinned GitHub open path was blocked by Colab's new-window behavior.
The same public notebook was uploaded as a private working copy. The T4 runtime, package version,
and CUDA availability above were observed in that copy. Its setup cell then stopped at the intended
precondition: `AssertionError: Không thấy data.yaml trong /`. No model checkpoint was downloaded,
no training data was uploaded, and no train/evaluation cell was run. Upload only the completed
`Day4-Lab/` folder after G-01, never protected gold or generated substitute labels. T4 remains
`POC required` until the complete post-label run records checkpoint, elapsed time, and generated
output.

## T-08 — Bộ face/hand, task B (G-03)

Chỉ ghi số đo. Kết luận core/stretch nằm ở bảng "Decisions pending owner" bên dưới.

| Mục | Giá trị |
| --- | --- |
| Thời gian dựng task B (tách khỏi annotate) | pending |
| Phút/ảnh (5 ảnh, 21+5 điểm) | pending |
| Tổng thời gian task B | pending |
| Tổng thời gian chặng 3 (18 ảnh task A + task B) | pending |
| Số lần sửa lại do nhầm topology 21/5 với 17 | pending |
| Thời gian export riêng; export task A có bị ảnh hưởng không | pending |

## T-10 — Timed run 240 phút (G-06)

Route Lane S của starter, checkpoint A–F theo bảng lịch trong `README.md`.

| Participant | A (0-20) | B (20-40) | C (40-130) | D (130-150) | E (150-190) | F (190-230) | Finish | Support requests | Đủ 9 deliverable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| novice/non-tech | | | | | | | | | pending |
| experienced | | | | | | | | | pending |


## Decisions pending owner

Không mục nào dưới đây được tự kích hoạt bởi runbook. Mỗi mục cần số đo trước, rồi owner chốt,
rồi mới sửa tài liệu và chạy lại gate liên quan.

| # | Quyết định | Số đo cần có | Phương án | Trạng thái |
| --- | --- | --- | --- | --- |
| DP-1 | Bộ face/hand (task B) là **core** hay **stretch** | T-08 | **đã khoá core** trong 90 phút chặng 3 | owner confirmed 2026-09-15 |
| DP-2 | Model và cấu hình train của lab | T-07 | **đã khoá** `yolo26n-pose.pt`, 80 epoch | owner confirmed 2026-09-15 |
| DP-3 | Số epoch nếu chặng 6 vượt 40 phút | T-07 | **giữ 80 epoch**; ghi vượt giờ nếu có | owner confirmed 2026-09-15 |
| DP-4 | Đổi lịch/timeline nếu 240 phút không đủ | T-10 | **giữ 240 phút / 7 chặng**, khối cabin nằm trong chặng 40-130; ghi vượt giờ nếu có | owner confirmed 2026-09-15 |
| DP-5 | Nhận commit baseline mới hơn `79f6724…` | T-02 `--allow-unpinned` | giữ pin · cập nhật pin | chưa đặt ra |
| DP-6 | Thang điểm dùng cho cohort | — | giữ thang baseline làm khởi đầu · sửa | owner giữ quyền |

## Release decision

- Trạng thái repo: `pilot-v0.4-alpha — ready to execute gates`
- Pilot test handoff: `ready`
- Freeze/student release: `hold`
- Blocking findings: G-01, G-02, G-03, G-04, G-06 (xem bảng tổng trạng thái)
- Decisions pending owner chưa chốt: DP-1 … DP-4
- Changes made and retested:
- Private reference location confirmed:
- Release sign-off:
