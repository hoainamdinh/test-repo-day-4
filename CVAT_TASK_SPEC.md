# CVAT task spec — evidence-ladder pilot v0.3

## Environment

- Dùng đúng CVAT classroom sẽ phục vụ cohort; ghi version trong `PILOT_RUN_SHEET.md`.
- Task type: Images, Shape mode.
- Task name đề xuất: `DAY04-POSE-PILOT-V03`.
- Images: đủ 10 file JPEG trong `data/images/`, đúng byte/hash và thứ tự manifest.

## Label

- Parent label: `person`
- Type: `skeleton`
- Sublabels: đúng 17 tên và thứ tự trong `data/schema/coco17-keypoints.json`
- Edges: đúng 19 cạnh.
- Không thêm hand/face schema, action attribute hoặc class khác.

Trong Skeleton Configurator, upload `data/schema/coco17-cvat-skeleton.svg`. Ở Raw/Constructor, xác nhận từng `data-label-name`; nếu CVAT version không nhận SVG, tạo thủ công từ JSON rồi download lại SVG thực tế và ghi chênh lệch. Không tạo task cho đến khi preflight pass vì skeleton không sửa được sau khi task tồn tại.

## Visibility mapping cần chứng minh bằng round-trip

| CVAT point state | COCO expected |
| --- | ---: |
| Visible | `v=2` |
| Occluded | `v=1` |
| Outside | `v=0` |

Technical POC phải tạo ít nhất một point ở mỗi state, save/reload, export COCO Keypoints 1.0 rồi kiểm JSON bằng validator. `Hidden` chỉ thay UI và không phải annotation state bền vững.

## Expected archive contract

- Đúng một `person_keypoints_*.json` hoặc một COCO annotation JSON trong ZIP.
- Mười image record có basename khớp manifest.
- Một annotation `person` trên mỗi image.
- Mỗi `keypoints` có 51 số; `num_keypoints == count(v > 0)`.
- Category có đúng 17 keypoint và 19 skeleton edge.
- Hai image record calibration phải có đủ 17 point được gán; tám image cabin phải giữ năm facial node ở `v=0`.
