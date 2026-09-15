# Pose review — Lane C

<!-- Template này dùng cho drill cabin 10 ảnh. Lane S nộp reports/REPORT.md và
     reports/review_partner.md theo mẫu của repo starter. -->

SELF_QC_COMPLETE: no
PEER_REVIEW_COMPLETE: no
REWORK_COMPLETE: no

## Self-QC

| Image | Topology/left-right evidence | Visibility evidence | Anatomy evidence |
| --- | --- | --- | --- |
| d04-01-calibration-full-coco17-frontal.jpg | TODO | TODO | TODO |
| d04-02-calibration-raised-arm-coco17.jpg | TODO | TODO | TODO |
| d04-03-cabin-real-vehicle-baseline.jpg | TODO | TODO | TODO |
| d04-04-cabin-real-vehicle-object-interaction.jpg | TODO | TODO | TODO |
| d04-05-cabin-real-vehicle-cool-cast.jpg | TODO | TODO | TODO |
| d04-06-cabin-real-vehicle-forward-lean.jpg | TODO | TODO | TODO |
| d04-07-cabin-real-vehicle-handheld-object.jpg | TODO | TODO | TODO |
| d04-08-cabin-simulator-low-light.jpg | TODO | TODO | TODO |
| d04-09-cabin-simulator-glare.jpg | TODO | TODO | TODO |
| d04-10-cabin-simulator-obstruction.jpg | TODO | TODO | TODO |

## Cabin data-quality triage

Không suy luận trạng thái tài xế. Với mỗi ảnh cabin, đánh giá **khả năng tạo nhãn pose đáng tin cậy**.

| Image | Decision | Evidence limitation | Affected keypoints | Downstream action |
| --- | --- | --- | --- | --- |
| d04-03-cabin-real-vehicle-baseline.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-04-cabin-real-vehicle-object-interaction.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-05-cabin-real-vehicle-cool-cast.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-06-cabin-real-vehicle-forward-lean.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-07-cabin-real-vehicle-handheld-object.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-08-cabin-simulator-low-light.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-09-cabin-simulator-glare.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |
| d04-10-cabin-simulator-obstruction.jpg | usable / usable-with-limitations / needs-review | TODO | TODO | keep / relabel / recollect |

## Peer review

| Image | Keypoint | Finding and rule | Suggested fix | Closure |
| --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | fixed / not-a-defect / needs-review |

Nếu không tìm thấy lỗi, ghi một row `no defect found after three passes` và nêu evidence của cả topology, visibility và anatomy.

## Rework

Ghi annotation nào đã đổi, lý do, và xác nhận đã re-export; nếu không đổi, giải thích vì sao finding là `not-a-defect`.
