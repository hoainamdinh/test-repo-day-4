# Hướng dẫn pilot COCO-17

Tài liệu này phục vụ **Lane C — cabin compatibility drill**, khối ~60 phút nằm trong chặng gán
nhãn (phút 40-130) của buổi lab 240 phút. Phần còn lại của route nằm ở `GUIDE.md` của repo
starter; pilot không fork nó. Xem `STARTER_ALIGNMENT.md` để biết ranh giới.

## 0. Luật chung — giống starter

Bốn luật dưới đây giống hệt starter, đừng học lệch:

- `left_*` và `right_*` là bên trái/phải của **người trong ảnh**, không phải bên màn hình.
- **Mọi người trong ảnh đều đủ 17 điểm.** Điểm không dùng được thì gắn cờ, không xoá.
- `v=2` nhìn thấy; `v=1` bị che nhưng **còn trong khung** — vẫn đặt chấm ước lượng, bật `Occluded` (`q`);
  `v=0` **ra ngoài mép ảnh** — không đặt chấm, bật `Outside` (`o`).
- Không dùng `Hidden` (`h`): nó không được lưu, điểm vẫn xuất ra `v=2` ở vị trí cũ mà không có cảnh báo.
- Bấm thẳng biểu tượng **Save** trên toolbar; `Ctrl+S` không nhận nếu focus không ở canvas.

## 0b. Điểm lệch của Lane C — đọc kỹ

Trên 8 ảnh cabin, `nose`, `left_eye`, `right_eye`, `left_ear`, `right_ear` bắt buộc `Outside`
(`v=0`) vì privacy mask đã xoá evidence; **không** đặt điểm vào giữa mask. Theo luật starter thì
những khớp này lẽ ra là `v=1`. Đây là mâu thuẫn có chủ ý và là lý do nhãn Lane C **không bao giờ**
được trộn vào tập train của starter (D-01).

Trên 2 ảnh calibration, đặt đủ 17 điểm theo evidence, gồm cả 5 điểm mặt — đó là chỗ duy nhất
trong pack này chấm tọa độ facial landmark.

Mỗi ảnh cabin chỉ annotate driver ROI; người/cánh tay còn sót ở rìa sau crop không thuộc target.
Ở Lane S thì ngược lại: **mọi người trong ảnh đều được gán**, kể cả ảnh 2-3 người.

Không xem YOLO, reference hoặc bài peer trước khi kết thúc independent attempt và self-QC.

## 1. Preflight

1. Đối chiếu task với `CVAT_TASK_SPEC.md` mục "Lane C".
2. Đếm 17 sublabel và kiểm `nose` ở index 0, `left_ankle` 15, `right_ankle` 16.
3. Mở đủ 10 ảnh, đối chiếu 10 participant code duy nhất và split 2 guided + 8 independent trong manifest.
4. Không tiếp tục nếu task đã tồn tại với schema khác; CVAT không cho sửa skeleton của task đã tạo.

## 2. Guided image

Làm hai ảnh `d04-01-calibration-full-coco17-frontal.jpg` và `d04-02-calibration-raised-arm-coco17.jpg`.

1. Draw new skeleton → **Shape** → `person`.
2. Đặt đủ 17 node, dùng hai ảnh này để calibration tên, topology, body-relative left/right và vị trí 5 facial node.
3. Joint bị che nhưng còn trong khung → `Occluded`; joint ngoài khung hoặc bị mask làm mất evidence → `Outside`.
4. Đọc tên từng điểm ở sidebar để bắt lỗi left/right.
5. Save, reload và kiểm skeleton vẫn giữ state.

Checkpoint B: giải thích được vì sao một điểm là `v=1`, không chỉ thao tác đúng nút.

## 3. Independent pack

Làm tám file `d04-03-cabin` đến `d04-10-cabin` độc lập, không mở diagnostic. Pack cố ý trộn
real-vehicle/simulator, object interaction, forward lean, low-light, glare và obstruction. Năm
facial node và mọi lower-body point ngoài khung phải là `Outside`; không kéo điểm vào mép ảnh để
“làm đủ”. Không nhập source behaviour class vào CVAT.

Trước khi annotate, dự đoán image nào `usable`, `usable-with-limitations` hoặc `needs-review`.
Sau self-QC, điền quyết định cuối vào `POSE_REVIEW.md`, nêu evidence limitation, keypoint bị ảnh
hưởng và action `keep/relabel/recollect`. Đây là quyết định về chất lượng dữ liệu pose, không
phải phân loại trạng thái tài xế.

## 4. Self-QC ba lượt

Thứ tự rẻ trước, đắt sau — giống chặng 4 của starter:

1. **Hình dáng:** đủ 17 tên, không swap trái/phải, edge nối hợp lý, không có xương kéo sang cơ thể khác.
2. **Đếm:** tách occluded khỏi outside; không dùng `v=0` để né điểm khó. Dấu hiệu hỏng: cả bài
   không có một khớp `v=1` nào.
3. **Phóng to:** chỉ 2-3 người mẫu, kiểm chấm lệch khỏi tâm khớp.

Ghi evidence vào bản copy của `reports/POSE_REVIEW_TEMPLATE.md` trước khi được mở diagnostic.

## 5. Export và audit

Task → Export task dataset → **COCO Keypoints 1.0** → Include images tùy chọn. Không đổi tên JSON
bên trong ZIP và không chỉnh JSON bằng tay.

```bash
python3 scripts/validate-submission.py --export COCO_KEYPOINTS_EXPORT.zip --write-report VISIBILITY_REPORT.csv
```

Structural PASS không thay self-QC.

Muốn đối chiếu với toolchain của lớp thì chạy thêm `tools/coco_kp_to_yolo_pose.py` và
`tools/check_pose_labels.py` của starter trên chính export này — nhưng nhớ rằng nó sẽ cảnh báo
5 facial node `v=0` của Lane C, và đó là **đúng theo D-01**, không phải lỗi người gán.

## 6. Diagnostic/peer/rework

Sau self-QC mới được chạy YOLO diagnostic. So sánh theo từng điểm; bất đồng chỉ tạo câu hỏi,
không biến model thành đáp án. Reviewer ghi ít nhất một finding, hoặc một no-defect row có ba pass
cụ thể. Tác giả quyết định `fixed`, `not-a-defect` hoặc `needs-review`, sửa trên CVAT và export
lại nếu annotation đổi.

## Recovery

- Sai schema: tạo task mới; không vá tên sau export.
- Không thấy COCO Keypoints: xác nhận label cha là `skeleton`, không phải 17 label point rời.
- Export ra file chỉ có `bbox`, không có `keypoints`: đã chọn nhầm **COCO 1.0** hoặc **YOLO 1.1**. Export lại.
- Validator báo sai filename: import đúng ảnh manifest, không đổi tên local.
- `num_keypoints` mismatch: kiểm state Outside/Occluded và export lại; không sửa JSON.
- Diagnostic lỗi tải model: bỏ qua; core không phụ thuộc model.
