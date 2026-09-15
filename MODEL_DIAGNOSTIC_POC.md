# Model runtime POC

Hai vai trò khác nhau, đừng lẫn:

- **Lane S** — model là *deliverable*: chặng 6 fine-tune trên Colab và nộp `outputs/eval_model.json`.
- **Lane C** — model là *diagnostic tùy chọn* sau self-QC, không phải ground truth, không nằm trong rubric core.

## Lane S — notebook baseline (gate G-04, chưa chạy)

`notebooks/day4_pose_finetune_yolo26.ipynb` trong `$STARTER`:

- `%pip -q install -U ultralytics` — **không pin version** (D-05);
- `MODEL_NAME = 'yolo26n-pose.pt'` (D-04);
- sinh `data_colab.yaml`, train 80 epoch, `seed=20260915`, `fliplr=0.5`;
- ghi `outputs/eval_model.json`.

Pilot **không fork notebook này**. Việc của pilot là chạy nó một lần trên Colab T4 và ghi lại:
version `ultralytics` thực tế cài được, checkpoint thực tế tải được, thời gian train 80 epoch,
và `eval_model.json` có sinh ra không. Thủ tục: `PILOT_TEST_RUNBOOK.md` mục T-07; chỗ ghi kết
quả: `PILOT_RUN_SHEET.md`.

Learning objective là model-neutral — và learning objective là **quyết định của owner pilot**,
không phải của baseline. Người học phải *giải thích* được con số, không phải làm nó đẹp. Thang
điểm đang dùng nói rõ `pose_mAP` thấp không bị trừ điểm — 20 ảnh là quá ít để fine-tune, và
`pose_mAP` có thể giảm sau fine-tune.

"Model-neutral" không có nghĩa là "không cần cấu hình lặp lại được". Owner đã khoá
`yolo26n-pose.pt` và 80 epoch để pilot mirror route người học. Nếu checkpoint không tải được,
T-07 ghi lỗi và G-04 fail; runbook không tự đổi sang `yolo11n-pose.pt`.

## Lane C — YOLO11 diagnostic POC (đã chạy)

Run date: 2026-09-14. Runtime: local macOS, Python 3.13, `ultralytics==8.4.145`,
`yolo11n-pose.pt` downloaded from the Ultralytics v8.4 asset release.

```bash
python3 scripts/run-yolo11-diagnostic.py --acknowledge-license-review
```

Result: exit 0 on both pilot images. Output overlays were written under ignored
`outputs/yolo11-diagnostic/`. The downloaded weight was removed after the run and is not part of
the pilot repository.

Visual finding: the model found one person with high confidence in each image, but inferred
lower-body joints at/near the crop boundary even where ankles were not visible. This is useful
evidence for the teaching order: learner attempt and self-QC first; model output later as a
fallible diagnostic, never as reference.

This POC proves runtime compatibility only. It does not validate CVAT export semantics,
annotation accuracy or enterprise license suitability — **và nó không thay được G-04**, vì nó
chạy khác model, khác version và khác phần cứng so với notebook baseline.

## Ràng buộc chung

- Không commit file `.pt` vào repo (test contract chặn).
- Không để model ghi đè annotation của người.
- Nhãn Lane C không bao giờ là input fine-tune (D-01).
