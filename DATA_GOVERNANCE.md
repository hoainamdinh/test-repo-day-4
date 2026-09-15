# Data governance — Day 4 pose v0.4

## Active classroom dataset (Lane S)

Lane S dùng 30 ảnh COCO val2017 (20 train + 10 test) với annotation CC BY 4.0 (ảnh là ảnh Flickr do COCO phân phối theo điều khoản riêng của COCO), lọc theo tiêu chí "người trong và quanh phương tiện", ngưỡng chiều cao bbox 40%.

Luật cứng:
- `$GOLD_RELEASE_DIR` (`gold_labels.zip`) chỉ được cung cấp cho học viên/Colab sau khi cả lớp đã hoàn thành và khoá nhãn (mốc phút 150).
- Gate G-05 kiểm tự động điều này (`scripts/check-starter-alignment.py`).

## Annotation boundary

Blur/mask đơn lẻ không tự động làm dữ liệu vô danh. Tọa độ bên dưới mask không được đánh giá.



## Release controls

Before each cohort:

1. run `python3 scripts/audit-data-pack.py`;
2. visually review every output for faces, plates, readable displays/documents and unintended identifiers;
3. verify the attribution/license notice remains with the data;
4. keep private reference annotations and student exports outside a public repository;
5. replace any image whose mask damages shoulder/elbow/wrist evidence or whose provenance becomes disputed.

The HSRD previews, Mendeley source archive and HADRIAN videos are retrieval inputs. Temporary raw material must be deleted after review. A starter repo may contain the 10 derivatives only while preserving attribution, change notices and the noncommercial restriction; otherwise it must distribute the retrieval/build script and pinned hashes.

## Sources excluded from bundling

- DriPE: technically excellent COCO-17 driver pose reference, but its licence prohibits third-party republication.
- DMD: academic/noncommercial plus NoDerivatives; no processed working copy is republished.
- Drive&Act/DD-Pose/other gated datasets: research access or redistribution conditions are not satisfied by this pilot.
- BML-MoVi: consented and usable for noncommercial education, but the licence prohibits third-party distribution without written permission.
- MEVA: CC BY 4.0 and IRB-reviewed, but tested example frames lacked enough facial resolution for the calibration objective.
- Web images without a specific reuse licence and privacy review.

This is an engineering data-handling contract, not legal advice. Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 has effect from 01/01/2026 and distinguishes genuine de-identification from data that can still identify a person: <https://congbao.chinhphu.vn/van-ban/luat-so-91-2025-qh15-45578.htm>.
