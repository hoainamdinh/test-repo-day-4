# Hướng dẫn pilot COCO-17

## Rule card

- `left_*` và `right_*` là bên trái/phải của **người trong ảnh**, không phải bên màn hình của annotator.
- `v=2`: điểm nhìn thấy và đặt tại tâm giải phẫu.
- `v=1`: điểm bị che nhưng vị trí có thể suy ra hợp lý; bật `Occluded` trong CVAT.
- `v=0`: điểm ngoài khung hoặc không thể gán; đặt sublabel `Outside`, không đoán vào mép ảnh.
- Mỗi ảnh chỉ annotate driver ROI; người/cánh tay còn sót ở rìa sau crop không thuộc target.
- Hai ảnh calibration: đặt đủ 17 điểm theo evidence nhìn thấy, bao gồm `nose`, hai mắt và hai tai.
- Tám ảnh cabin: `nose`, hai mắt và hai tai phải là `Outside` vì privacy mask làm mất evidence; không đặt vào giữa mask.
- Không xem YOLO, reference hoặc bài peer trước khi kết thúc independent attempt và self-QC.

## 1. Preflight

1. Đối chiếu task với `CVAT_TASK_SPEC.md`.
2. Đếm 17 sublabel và kiểm `nose` ở index 0, `left_ankle` 15, `right_ankle` 16.
3. Mở đủ 10 ảnh, đối chiếu 10 participant code duy nhất và split 2 guided + 8 independent trong manifest.
4. Không tiếp tục nếu task đã tồn tại với schema khác; CVAT không cho sửa skeleton của task đã tạo.

## 2. Guided image

Làm hai ảnh `d04-01-calibration-full-coco17-frontal.jpg` và `d04-02-calibration-raised-arm-coco17.jpg`.

1. Draw new skeleton → Shape → `person`.
2. Đặt đủ 17 node, dùng hai ảnh này để calibration tên, topology, body-relative left/right và vị trí 5 facial node.
3. Với joint bị che nhưng vị trí còn suy ra được, dùng `Occluded`; với joint ngoài khung hoặc bị mask làm mất evidence, dùng `Outside`.
4. Đọc tên từng điểm ở sidebar để bắt lỗi left/right.
5. Save, reload và kiểm skeleton vẫn giữ state.

Checkpoint B: giải thích được vì sao một điểm là `v=1`, không chỉ thao tác đúng nút.

## 3. Independent pack

Làm tám file `d04-03-cabin` đến `d04-10-cabin` độc lập, không mở diagnostic. Pack cố ý trộn real-vehicle/simulator, object interaction, forward lean, low-light, glare và obstruction. Năm facial node và mọi lower-body point ngoài khung phải là `Outside`; không kéo điểm vào mép ảnh để “làm đủ”. Không nhập source behaviour class vào CVAT.

Trước khi annotate, dự đoán image nào `usable`, `usable-with-limitations` hoặc `needs-review`. Sau self-QC, điền quyết định cuối vào `POSE_REVIEW.md`, nêu evidence limitation, keypoint bị ảnh hưởng và action `keep/relabel/recollect`. Đây là quyết định về chất lượng dữ liệu pose, không phải phân loại trạng thái tài xế.

## 4. Self-QC ba lượt

1. **Topology/identity:** đủ 17 tên, không swap trái/phải, edge nối hợp lý.
2. **Visibility:** xem từng điểm, tách occluded khỏi outside; không dùng `v=0` để né điểm khó.
3. **Anatomy/geometry:** điểm nằm trên joint, không floating trên ghế/volant; pose nhất quán với chi nhìn thấy.

Ghi evidence vào bản copy của `reports/POSE_REVIEW_TEMPLATE.md` trước khi được mở diagnostic.

## 5. Export và audit

Task → Export task dataset → **COCO Keypoints 1.0** → Include images tùy chọn. Không đổi tên JSON bên trong ZIP và không chỉnh JSON bằng tay.

Chạy notebook hoặc CLI. Structural PASS không thay self-QC.

## 6. Diagnostic/peer/rework

Sau self-QC mới được chạy YOLO diagnostic. So sánh theo từng điểm; bất đồng chỉ tạo câu hỏi, không biến model thành đáp án. Reviewer ghi ít nhất một finding, hoặc một no-defect row có ba pass cụ thể. Tác giả quyết định `fixed`, `not-a-defect` hoặc `needs-review`, sửa trên CVAT và export lại nếu annotation đổi.

## Recovery

- Sai schema: tạo task mới; không vá tên sau export.
- Không thấy COCO Keypoints: xác nhận label cha là `skeleton`, không phải 17 label point rời.
- Validator báo sai filename: import đúng ảnh manifest, không đổi tên local.
- `num_keypoints` mismatch: kiểm state Outside/Occluded và export lại; không sửa JSON.
- Diagnostic lỗi tải model: bỏ qua; core không phụ thuộc model.
