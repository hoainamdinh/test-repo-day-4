# Pilot data — Lane C only

Thư mục này chỉ phục vụ **Lane C (cabin compatibility drill)**. Dataset của lớp học nằm ở
`dataset/` của repo starter và không bao giờ trộn với pack này — xem `STARTER_ALIGNMENT.md` D-01
và gate G-05.

- `images/`: 2 consented full-body calibration crops + 8 privacy-reduced cabin derivatives, from 10 people and 3 sources; no AI-generated media.
- `image-manifest.csv`: filename, participant, source, licence, processing, dimensions and output SHA-256 contract.
- `source-selection.json`: maintainer retrieval selectors, source integrity references, crops/masks and stressors.
- `GENERATION_RECORD.md`: selection/processing record; name retained for repository compatibility.
- `schema/coco17-keypoints.json`: canonical names, flip map and COCO 1-indexed edges.
- `schema/coco17-cvat-skeleton.svg`: uploadable CVAT skeleton template.

Do not add raw source archives, videos, private reference annotations or student submissions. Run `../scripts/audit-data-pack.py` before creating the CVAT task and follow `../DATA_GOVERNANCE.md`.
