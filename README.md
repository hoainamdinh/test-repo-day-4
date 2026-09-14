# Day 4 pilot — Cabin pose keypoints

> **Trạng thái:** sẵn sàng kiểm thử. Local CVAT Docker v2.74.1 đã pass task/schema/order smoke trên task #16/job #12; semantic round-trip và timed dry-run vẫn là release gate trước khi freeze.

Đây là pilot của lab **240 phút** về COCO-17 pose annotation. Active pack gồm 10 người khác nhau theo hai evidence lane và được khóa bằng contract `pilot-v0.3` sau khi hoàn tất kiểm thử.

Mở `lab-guide.html` để dùng hướng dẫn trực quan, responsive, checklist preflight tương tác và tutorial CVAT có ảnh chụp thật. `GUIDE.md` là bản chữ tương đương để tra cứu nhanh.

## Quyết định dữ liệu

- **Calibration lane:** 2 crop full-body từ HSRD-100, hai participant khác nhau, informed consent + CC BY 4.0. Mặt đủ rõ để học viên thực sự đặt đủ 17 COCO keypoint.
- **Cabin lane:** 5 ảnh/5 recording ID từ Driver Risk Behavior Dataset và 3 frame/3 participant ID từ HADRIAN. Đây là 8 ảnh independent về occlusion, field-of-view, ánh sáng và labelability.
- Không có ảnh AI trong active pack. Validator bắt buộc đúng 10 người, 3 nguồn, split 2 guided + 8 independent và không quá 3 ảnh từ cùng một setup/camera.
- Ảnh Mendeley được crop vào driver ROI và che mặt; frame HADRIAN giữ face mask của tác giả. Tất cả output được tái tạo từ pixel, không mang EXIF/ICC/XMP/comment, và khóa SHA-256 trong manifest.
- Pack chỉ dùng trong lane lớp học/phi thương mại do giới hạn CC BY-NC của HADRIAN. “Đã mask” không đồng nghĩa “anonymous”. Năm điểm `nose/eyes/ears` được chấm tọa độ trên 2 ảnh calibration; trên 8 ảnh cabin chúng bắt buộc `Outside` (`v=0`) và không được chấm vị trí.
- Source behaviour label chỉ nằm trong provenance để truy vết, không phải ground truth của lab; học viên không được kết luận distracted/drowsy từ một still frame.
- DriPE, DMD và Drive&Act chỉ là benchmark nghiên cứu khi điều khoản không cho phép bundle working copy.
- Reference annotation được giữ ngoài repo; không có answer key ẩn hoặc nhãn giả trong pilot.

Xem `DATA_GOVERNANCE.md` trước khi thay bất kỳ ảnh nào.

## Learning objective

Sau lab, người học có thể:

1. Tạo một skeleton `person` theo đúng thứ tự COCO-17.
2. Phân biệt `v=0` ngoài khung/không gán, `v=1` bị che nhưng suy ra được và `v=2` nhìn thấy.
3. Hoàn thành independent attempt trước khi xem model/reference hoặc bài của peer.
4. Tự kiểm topology, trái/phải, visibility và vị trí giải phẫu.
5. Viết finding có ảnh–keypoint–rule–fix, rework rồi export COCO Keypoints.
6. Kiểm cấu trúc artifact mà không nhầm structural PASS với semantic ground truth.
7. Đưa ra quyết định `usable / usable-with-limitations / needs-review` cho dữ liệu pose và đề xuất `keep / relabel / recollect` bằng evidence.

## Lịch lab 240 phút

| Phút | Hoạt động | Evidence/checkpoint |
| ---: | --- | --- |
| 0-15 | Mục tiêu, privacy boundary, preflight task/schema | A — đúng task và đúng 17 điểm |
| 15-35 | Demo COCO-17, trái/phải và `v=0/1/2` | gọi đúng 17 tên và ba visibility state |
| 35-55 | Error clinic: swap, floating joint, occlusion, out-of-frame | chẩn đoán 4 lỗi mẫu |
| 55-80 | Guided annotation trên 2 ảnh mẫu | B — skeleton hợp lệ |
| 80-90 | Nghỉ | — |
| 90-105 | Đọc pack chính, prediction và annotation plan | chọn thứ tự 8 ảnh independent |
| 105-155 | Independent annotation, chưa xem model/reference | C — đủ 8 skeleton |
| 155-175 | Self-QC ba lượt và rework | D — log topology/visibility/anatomy |
| 175-190 | Export COCO Keypoints và chạy structural audit | E — ZIP + visibility report |
| 190-200 | Nghỉ | — |
| 200-210 | Mở model diagnostic hoặc lỗi mẫu để calibration | model chỉ là diagnostic |
| 210-225 | Peer review có evidence | F — finding hoặc no-defect row hợp lệ |
| 225-237 | Tác giả xử lý finding, re-export | mọi finding có closure |
| 237-240 | Kiểm bộ nộp và exit ticket | đủ ba artifact |

Pack 10 ảnh đã đủ cho timed dry-run, nhưng chưa phải production/fairness dataset. Chỉ được tuyên bố lab khả thi sau khi novice và experienced learner hoàn thành cùng contract trong 240 phút.

## Chạy pilot nhanh

1. Chạy `python3 scripts/audit-data-pack.py`, rồi tạo task trên CVAT Docker local với đủ 10 ảnh trong `data/images/`.
2. Import `data/schema/coco17-cvat-skeleton.svg`, xác nhận đủ 17 sublabel đúng thứ tự rồi mới tạo task.
3. Làm ảnh guided, sau đó ảnh independent theo `GUIDE.md`.
4. Export **COCO Keypoints 1.0** thành `COCO_KEYPOINTS_EXPORT.zip`.
5. Chạy:

```bash
python3 scripts/validate-submission.py --export COCO_KEYPOINTS_EXPORT.zip --write-report VISIBILITY_REPORT.csv
```

6. Điền `reports/POSE_REVIEW_TEMPLATE.md`, lưu thành `POSE_REVIEW.md`, rồi kiểm đủ bộ:

```bash
python3 scripts/validate-submission.py --submission-dir submission
```

Notebook `notebooks/day4-pose-quality.ipynb` cung cấp cùng quy trình cho Colab và không yêu cầu người học viết code.

POC cũ trên task #14/job #10 chỉ chứng minh round-trip schema/export của hai ảnh đã retire. Pack v0.3 đã pass task/schema/order smoke trên task #16/job #12; annotation/save-reload/export semantic round-trip vẫn phải hoàn tất. Annotation POC không phải reference.

## Bộ nộp

ZIP cuối mở ra phải có đúng ba file ở root:

```text
COCO_KEYPOINTS_EXPORT.zip
VISIBILITY_REPORT.csv
POSE_REVIEW.md
```

Validator chỉ chứng minh cấu trúc, schema, image mapping và consistency của visibility count. Nó không chứng minh keypoint nằm đúng giải phẫu; semantic quality phải qua self-QC, peer review và reference riêng tư.

## Model diagnostic

`yolo11n-pose.pt` được giữ làm diagnostic tùy chọn sau self-QC vì không đổi learning objective. Dependency được pin `ultralytics==8.4.145`; weight không nằm trong repo. Phải đọc `THIRD_PARTY_NOTICES.md` và xác nhận license boundary trước khi chạy script.

```bash
python3 scripts/run-yolo11-diagnostic.py --acknowledge-license-review
```

Model output không phải ground truth, không tự động ghi đè annotation và không thuộc rubric core.

## Release gate

Chỉ freeze `pilot-v0.3` sau khi CVAT Docker semantic round-trip và timed dry-run đều pass. Mọi thay đổi learning objective, schema, order, evidence, privacy boundary hoặc thời lượng 240 phút phải quay lại vòng pilot và kiểm thử tương ứng.
