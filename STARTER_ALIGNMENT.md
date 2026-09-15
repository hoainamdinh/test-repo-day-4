# Starter compatibility contract — Day 4

Repo starter: <https://github.com/VinUni-AI20k/Day4-TrackData-Keypoint-Pose>.
Bản đối chiếu này được xác minh trên commit đã pin `79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3`
(2026-09-15). Đổi pin là một quyết định có chủ ý, không phải việc chạy `git pull`.

## 0. Starter là gì trong pilot này

Starter là **technical compatibility baseline**: nó định nghĩa các bất biến kỹ thuật mà bài nộp
phải khớp để chạy được cùng một toolchain — schema 17 điểm, `kpt_shape: [17, 3]`, `flip_idx`,
định dạng export COCO Keypoints 1.0, 56 số/dòng YOLO Pose, cách tính OKS, cấu trúc asset skeleton.

Starter **không** giữ quyền quyết định về lab. Những thứ sau là quyết định của owner pilot, và
pilot chịu trách nhiệm cuối:

| Quyết định | Ai quyết | Ghi chú |
| --- | --- | --- |
| Timeline và ngân sách thời lượng | **owner pilot** | lịch hiện tại mirror 7 chặng của starter vì đang *kiểm chứng* nó, không phải vì bị buộc |
| Learning objective | **owner pilot** | |
| Rubric và cổng chấm | **owner pilot** | đang dùng thang của starter làm điểm khởi đầu; đổi thang là quyền của owner |
| Bộ face/hand là core hay stretch | **owner pilot** | owner đã khoá **core**, chạy trong chặng 40-130; T-08 chỉ đo khả năng thực thi |
| Model và cấu hình train | **owner pilot** | owner đã khoá `yolo26n-pose.pt`, 80 epoch; T-07 chỉ đo khả năng thực thi |
| Quyết định freeze/release | **owner pilot** | `PILOT_RUN_SHEET.md` |
| Privacy/governance ảnh cabin | **owner pilot** | lane riêng, xem mục 3 |
| Schema keypoint, định dạng export, công thức OKS | **baseline kỹ thuật** | đổi là mất tương thích — phải ghi vào mục 4 |
| Dataset lớp học (20 train + 10 test), gold | **baseline kỹ thuật** | pilot đọc tại chỗ, không tạo bản thay thế |
| Toolchain chấm (`tools/*.py`) | **baseline kỹ thuật** | pilot không fork — tránh hai định nghĩa OKS |

Nguyên tắc vận hành: **pilot không tái cài đặt thứ starter đã có sẵn và đang chạy được.** Khi
pilot lệch khỏi baseline, ghi vào mục 4 kèm lý do và gate. Khi owner muốn đổi timeline hay
rubric, đó là thay đổi hợp lệ — chỉ cần ghi lại, không cần starter cho phép.

## 1. Từ vựng trung tính

Tài liệu và script trong pilot dùng các tên sau thay cho tên vai trò:

| Ký hiệu | Nghĩa |
| --- | --- |
| `$STARTER` | checkout repo starter; luôn truyền qua `--starter`, tài liệu này dùng `../tmp/day4-starter` |
| `$STARTER_ASSETS_DIR` | thư mục chứa `labels_day4.json` và 3 file skeleton SVG |
| `$GOLD_RELEASE_DIR` | **protected gold release** — thư mục gold chỉ được mở sau khi nhãn đã khoá |
| `$PROTECTED_SOURCE_DIR` | provenance/mapping nguồn của dataset, không phát ra ngoài |

`scripts/check-starter-alignment.py` tự tìm `$STARTER_ASSETS_DIR` và `$GOLD_RELEASE_DIR` theo
hình dạng thư mục, nên pilot không phụ thuộc vào cách starter đặt tên đường dẫn.

## 2. Lane S của pilot

| Hạng mục | Lane S — starter route |
| --- | --- |
| Mục đích | Chạy thử đúng trải nghiệm người học |
| Dữ liệu | `dataset/images/train` + `test` (20 train + 10 test) |
| Người/ảnh | 29 người trên 20 ảnh (1-3 người/ảnh) |
| Task CVAT | **Hai task**: A = 20 ảnh/`person`; B = 5 ảnh/`hand`+`face` |
| Facial keypoint | Theo evidence, `v` bình thường |
| Chấm | OKS với protected gold release (`gold_labels.zip`) |
| Thời lượng | 240 phút (mốc đang kiểm chứng) |
| Bộ nộp | 9 deliverable |

## 3. Mapping artifact

| Starter | Pilot tương ứng | Trạng thái |
| --- | --- | --- |
| `README.md` (bộ nộp 9 mục) | `README.md` mục "Bộ nộp Lane S" | mirror |
| `GUIDE.md` (7 chặng) | `README.md` lịch Lane S | mirror để kiểm chứng |
| `GUIDELINE_MINI.md` | không fork | dùng trực tiếp file của starter |
| `RUBRIC.md` | `RUBRIC.md` (readiness) | tách vai trò |
| `reports/REVIEWER_CHECKLIST.md` | dùng trực tiếp | — |
| `tools/*.py` gồm `evaluate_pose_annotations.py` | không fork | `scripts/check-starter-alignment.py` kiểm sự tồn tại/định dạng/finding |
| `notebooks/day4_pose_finetune_yolo26.ipynb` | `notebooks/day4_pose_finetune_yolo26.ipynb` | Colab notebook fine-tune |
| `$STARTER_ASSETS_DIR` (`labels_day4.json`, 3 SVG) | `data/schema/coco17-*.{json,svg}` | topology đã đối chiếu trùng khớp |
| `$GOLD_RELEASE_DIR`, `$PROTECTED_SOURCE_DIR` | `gold_labels.zip` | `REFERENCE_REVIEW_PROTOCOL.md` |
| `dataset/labels/test/*.txt` | `dataset/labels/test/` | tập test baseline |

## 4. Divergence register

| ID | Lệch ở đâu | Quyết định | Gate |
| --- | --- | --- | --- |
| D-02 | Pilot từng chỉ có 1 skeleton/ảnh; dataset lớp có 29 người trên 20 ảnh | bổ sung multi-person drill; lỗi trọng tâm là `nham_nguoi` và `dao_trai_phai` | G-02 |
| D-03 | Pilot dừng ở COCO ZIP + CSV + review; route đầy đủ đi tiếp tới YOLO Pose, gold, model | pilot chạy trọn 7 chặng để kiểm chứng | G-01 |
| D-04 | Notebook baseline dùng `yolo26n-pose.pt` | objective model-neutral; owner đã khoá `yolo26n-pose.pt` để pilot mirror notebook baseline | G-04 |
| D-05 | Notebook cài `%pip install -U ultralytics` không pin | pilot ghi lại version Colab thực tế, không sửa notebook của starter | G-04 |
| D-06 | Bộ face/hand 21+5 điểm, 5 ảnh, task CVAT riêng | **owner chốt** core hay stretch sau khi có số đo thời lượng | G-03 |
| D-07 | Starter mặc định app.cvat.ai; `From model → Human pose estimation` không có trên self-hosted trần | pilot chứng minh đường `labels_day4.json` và `.svg` trên CVAT Docker | G-02 |
| D-08 | `check_pose_labels.py` cảnh báo ngay trên chính gold/test của starter | **là hành vi đúng, không phải lỗi** — 8 cảnh báo ở train, 4 ở test | đã xác minh |

## 5. Bằng chứng đã xác minh (2026-09-15, local)

Chạy trên checkout starter ở commit đã pin, Python 3.13, stdlib:

| Kiểm | Kết quả |
| --- | --- |
| `check_pose_labels.py` trên `$GOLD_RELEASE_DIR/labels/train` | ĐẠT định dạng, **8** cảnh báo `v=0` giữa khung |
| `check_pose_labels.py` trên `dataset/labels/test` | ĐẠT định dạng, **4** cảnh báo |
| `make_mock_student.py --quality average` → `evaluate_pose_annotations.py` | 29/29 người khớp, mean OKS `0.6921`, OKS@0.50 `0.8621`, OKS@0.75 `0.5172` |
| Findings của bài `average` | `dao_trai_phai` 4, `nham_nguoi` 2, `xoa_khop_bi_che` 17, `gold_khong_gan_nhan` 8 |
| Topology | 17 tên và 19 cạnh của `tools/poselib.py` trùng `data/schema/coco17-keypoints.json` (starter 0-indexed, pilot 1-indexed COCO) |
| `flip_idx` | `data.yaml` của starter trùng schema pilot |
| Skeleton assets | `labels_day4.json` có đúng 3 skeleton 17/21/5; đủ 3 SVG |

Ba con số OKS trên khớp bảng ba mức chất lượng mà starter công bố, nên thang đó đang đúng với
dữ liệu hiện tại.

Chạy lại bất cứ lúc nào:

```bash
python3 scripts/check-starter-alignment.py --starter ../tmp/day4-starter
```

Checker **fail** nếu HEAD của checkout khác commit đã pin. Muốn khảo sát commit mới thì chạy
`--allow-unpinned`, rồi cập nhật pin trong script + hai tài liệu này/`PILOT_RUN_SHEET.md` nếu
quyết định nhận commit đó.

## 6. Gate chặn freeze

| ID | Gate | Trạng thái |
| --- | --- | --- |
| G-01 | Lane S đi trọn 7 chặng: CVAT → COCO Keypoints 1.0 → YOLO Pose → check → visibility → khoá → gold → rework → Colab → `eval_model.json` | pending |
| G-02 | Multi-person drill trên CVAT Docker: task A 20 ảnh, ảnh 2-3 người, save/reload/export giữ đúng định danh người | pending |
| G-03 | Đo thời lượng thật của task B (5 ảnh, `hand` 21 + `face` 5) và trình số liệu để owner chốt core/stretch | pending |
| G-04 | Chạy notebook baseline trên Colab T4, ghi version ultralytics/model thực tế, sinh được `eval_model.json` | pending |
| G-05 | Kiểm bất biến compatibility (dataset, `data.yaml`, 6 tool, evaluator, skeleton assets, commit pin) | tự động, xem `scripts/check-starter-alignment.py` |
| G-06 | Timed dry-run 240 phút, một novice và một learner có kinh nghiệm, trọn route Lane S; báo cáo nếu vượt giờ | pending |

Trạng thái hiện tại: **`pilot-v0.4-alpha — ready to execute gates`**. Chưa phải `release-ready`:
G-01, G-02, G-03, G-04 và G-06 vẫn pending.

Chi tiết cách chạy từng gate: `PILOT_TEST_RUNBOOK.md`. Ghi kết quả vào `PILOT_RUN_SHEET.md`.
