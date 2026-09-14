# Rubric formative — Day 4

Tất cả route dùng cùng chuẩn. Model/stretches không cộng điểm.

| Tiêu chí | Đạt | Cần rework |
| --- | --- | --- |
| Schema và coverage | đúng `person`, đủ 17 node theo thứ tự; một driver skeleton/ảnh | sai tên/thứ tự, thiếu/thừa skeleton |
| Calibration đủ COCO-17 | 2 ảnh guided có đủ 17 tọa độ, đúng facial landmark, topology và body-relative left/right | bỏ facial point dù còn evidence, hoặc đặt sai landmark |
| Cabin privacy/visibility | 8 ảnh cabin giữ năm facial nodes ở `v=0`; joint còn lại dùng `v=0/1/2` theo evidence | đặt facial point vào mask, đoán điểm ngoài khung, nhầm occluded/outside |
| Anatomy và left/right | point bám joint, không swap bên của subject | floating joint, swap trái/phải, geometry vô lý |
| Data-quality judgement | mỗi ảnh cabin có decision, limitation, keypoint bị ảnh hưởng và action nhất quán | gán nhãn trạng thái tài xế, hoặc quyết định không có evidence/action |
| Independent/self-QC | hoàn thành independent trước diagnostic và ghi đủ ba pass | xem model/reference sớm hoặc attestation thiếu |
| Peer evidence/rework | finding có image–keypoint–rule–fix và closure | nhận xét chung chung, không xử lý finding |
| Artifact | ba file đúng tên; structural validator PASS | sửa JSON tay, thiếu report hoặc ZIP không hợp lệ |

Structural PASS không tự động cho kết quả “Đạt”. Semantic verdict thuộc reviewer đã calibration và reference riêng tư.

Chấm độ chính xác vị trí `nose/left_eye/right_eye/left_ear/right_ear` trên đúng 2 ảnh calibration. Trên 8 ảnh cabin, chấm việc đặt chúng `Outside` đúng contract, không chấm tọa độ bên dưới mask.
