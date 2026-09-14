# Lab Coach test runbook — Day 4 pilot

## T-01 — Repository contract

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: toàn bộ test pass; notebook rebuild byte-for-byte giống nhau.

## T-02 — Data pack

```bash
python3 scripts/audit-data-pack.py
```

Expected: 10 JPEG đúng dimensions/hash, 10 participant code duy nhất, 3 nguồn, split 2 full-COCO17 guided + 8 cabin independent, không quá 3 ảnh/setup, không EXIF/ICC/XMP/comment và toàn pack khóa `classroom-noncommercial`.

## T-03 — CVAT round-trip

POC schema/export cũ: **pass** trên local Docker ngày 2026-09-14; xem `POC_CVAT_COCO_ROUNDTRIP.md`. Evidence-ladder pack v0.3 đã pass task/schema/order smoke trên task #16/job #12; các bước semantic dưới đây vẫn phải hoàn tất trước freeze.

1. Ghi URL/version/build của CVAT classroom vào `PILOT_RUN_SHEET.md`.
2. Tạo task mới đúng `CVAT_TASK_SPEC.md`, upload SVG và đủ 10 ảnh.
3. Trên hai ảnh guided, đặt và kiểm đủ 17 point; chứng minh facial landmark và body-relative left/right có thể chấm được.
4. Trên ít nhất một real-vehicle image và một simulator image, kiểm ankle/knee theo evidence thay vì theo thói quen.
5. Save/reload; export COCO Keypoints 1.0.
6. Chạy validator; mở visibility CSV và đối chiếu trực tiếp ba point vừa kiểm.
7. Re-import export vào task mới có cùng schema **chỉ nếu** classroom workflow dự kiến có import.

Fail nếu tên/thứ tự sublabel đổi, `v` mapping sai, filename không giữ hoặc UI guide không khớp. Sửa contract/guide và chạy lại; không bảo sinh viên sửa JSON.

## T-04 — Semantic pilot

Hai reviewer annotate độc lập theo `REFERENCE_REVIEW_PROTOCOL.md`. Reconcile nhưng giữ reference ngoài repo. Kiểm full-17 calibration trên HSRD; kiểm left/right, face-mask boundary, wrist occlusion và lower-body Outside trên cả hai nguồn cabin; thay ảnh nếu mask che mất vai/khuỷu hoặc scenario không tạo giá trị học tập.

## T-05 — Model diagnostic

Chỉ chạy sau khi bản human attempt đã khóa. Ghi Python, Ultralytics version, model checksum/source và output location. Xác nhận model có thể sai và không ghi đè CVAT. Nếu license/runtime không phù hợp, đánh dấu `not-run`; core vẫn pass.

## T-06 — Timed 240-minute dry-run (blocking cho full release)

Chạy nguyên pack 2 guided + 8 independent:

- một learner mới/non-tech;
- một learner có kinh nghiệm;
- cùng schema, evidence và rubric;
- ghi checkpoint A–F, số lần hỗ trợ, rework và thời gian hoàn tất.

Fail nếu novice không hoàn thành core trước phút 240. Ưu tiên giảm mật độ/mơ hồ của pack hoặc cải thiện đúng support step; không hạ evidence contract.

## T-07 — Freeze và instructor handoff

Chỉ sau T-01 đến T-06 pass, Lab Coach gắn `pilot-v0.3` và bàn giao:

- immutable image manifest/hashes;
- schema JSON/SVG;
- notebook/validator tests;
- learner flow, rubric và three-file submission contract;
- attribution/license notice, privacy transformations và danh sách private assets **không** được đưa vào repo.

Giảng viên mở PR starter repo. Lab Coach review PR và xác nhận không đổi learning objective, schema, order, evidence, privacy boundary hoặc 240 phút.
