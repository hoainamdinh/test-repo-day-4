# Rubric readiness — pilot Day 4

**Đây không phải rubric chấm người học.** Rubric chấm điểm là **quyết định của owner pilot**
(`STARTER_ALIGNMENT.md` mục 0, DP-6). Hiện owner đang dùng thang của baseline kỹ thuật làm điểm
khởi đầu — 100 điểm kèm cổng bắt buộc — và pilot **không** viết lại nó, vì hai bảng điểm song
song là cách nhanh nhất để lớp chấm lệch nhau. Đổi thang là thay đổi hợp lệ: chỉ cần owner ghi
lại, không cần baseline cho phép.

File này chấm **độ sẵn sàng của pilot**: mỗi dòng là một thứ phải chứng minh được trước khi
owner cân nhắc freeze `pilot-v0.4`.

## Cổng của thang điểm đang dùng mà pilot phải đo được

Pilot phải chạy được đến chỗ quan sát trực tiếp các cổng dưới đây, không suy đoán:

| Cổng | Pilot chứng minh bằng |
| --- | --- |
| OKS trung bình ≥ 0.75 **và** OKS@0.75 ≥ 0.70 | `outputs/eval_vs_gold.json` của lần dry-run Lane S |
| Không còn lỗi `dao_trai_phai` nào | mục `findings` trong cùng file, sau rework |
| Export sai định dạng → trần 40 điểm | thử export nhầm **COCO 1.0** một lần để xác nhận validator bắt được |
| `kpt_shape: [17, 2]` → trần 40 điểm | đã tự động hoá trong `scripts/check-starter-alignment.py` |
| Không có `eval_vs_gold.json` → trần 69 điểm | mốc phát gold (phút 150) phải khả thi trong timed run |
| Chạy model trước khi khoá nhãn → không tính annotation | thứ tự chặng 4 → 5 → 6 giữ được trong 240 phút |

Ba mức chất lượng của thang này (xuất sắc ≥ 0.85 / đạt ≥ 0.75 / rework < 0.75) đã được xác minh
lại bằng `make_mock_student.py` — xem `STARTER_ALIGNMENT.md` mục 5.

## Readiness của Lane S

| Hạng mục | Sẵn sàng | Chưa sẵn sàng |
| --- | --- | --- |
| Route đầy đủ (G-01) | đi hết CVAT → COCO KP 1.0 → YOLO Pose → check → visibility → khoá → gold → rework → Colab → `eval_model.json` | còn chặng chưa ai chạy thật |
| Multi-person (G-02) | 29 người trên 20 ảnh, `train_13` giữ đúng 3 skeleton qua save/reload/export | chỉ thử ảnh 1 người |
| Face/hand (G-03) | task B chạy thật, có số phút cho 5 ảnh 21+5 điểm và export riêng; owner đã chốt core/stretch (DP-1) | chưa có số đo, hoặc để runbook tự cắt |
| Colab (G-04) | một lần chạy T4 thành công, ghi version `ultralytics` và model thực tế lấy được | chỉ có POC local |
| Lane separation (G-05) | `check-starter-alignment.py` PASS | có ảnh/nhãn/gold đi nhầm lane |
| Timed run (G-06) | 240 phút với một novice và một learner có kinh nghiệm | mới ước lượng trên giấy |

## Readiness của Lane C

| Hạng mục | Sẵn sàng | Chưa sẵn sàng |
| --- | --- | --- |
| Schema và coverage | đúng `person`, đủ 17 node theo thứ tự; một driver skeleton/ảnh | sai tên/thứ tự, thiếu/thừa skeleton |
| Calibration đủ COCO-17 | 2 ảnh guided có đủ 17 tọa độ, đúng facial landmark, topology và body-relative left/right | bỏ facial point dù còn evidence, hoặc đặt sai landmark |
| Cabin privacy/visibility | 8 ảnh cabin giữ năm facial node ở `v=0` (D-01); joint còn lại dùng `v=0/1/2` theo evidence | đặt facial point vào mask, đoán điểm ngoài khung, nhầm occluded/outside |
| Anatomy và left/right | point bám joint, không swap bên của subject | floating joint, swap trái/phải, geometry vô lý |
| Data-quality judgement | mỗi ảnh cabin có decision, limitation, keypoint bị ảnh hưởng và action nhất quán | gán nhãn trạng thái tài xế, hoặc quyết định không có evidence/action |
| Independent/self-QC | hoàn thành independent attempt trước diagnostic và ghi đủ ba pass | xem model/reference sớm hoặc attestation thiếu |
| Peer evidence/rework | finding có image–keypoint–rule–fix và closure | nhận xét chung chung, không xử lý finding |
| Artifact | ba file đúng tên; structural validator PASS | sửa JSON tay, thiếu report hoặc ZIP không hợp lệ |

Structural PASS không tự động cho kết quả "Đạt". Semantic verdict thuộc reviewer đã calibration
và reference riêng tư — `REFERENCE_REVIEW_PROTOCOL.md`.

Chấm độ chính xác vị trí `nose/left_eye/right_eye/left_ear/right_ear` trên đúng 2 ảnh
calibration. Trên 8 ảnh cabin, chấm việc đặt chúng `Outside` đúng contract, không chấm tọa độ
bên dưới mask.

**Điểm lệch cần nói rõ với người học:** luật `v=0` của Lane C ngược với luật của baseline. Nếu
drill này được dùng trong lớp, phải nói trước rằng đó là ngoại lệ do privacy, không phải luật
chung — nếu không, người học mang thói quen `v=0` sai sang bài chấm.
