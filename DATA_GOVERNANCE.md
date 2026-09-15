# Data governance — Day 4 pose v0.4

## Lane separation (bắt buộc)

Pilot có hai tập dữ liệu, thuộc hai chủ sở hữu khác nhau, **không được trộn**:

| | Lane S | Lane C |
| --- | --- | --- |
| Dữ liệu | 20 train + 10 test của starter (COCO val2017 subset) | 10 ảnh trong `data/images/` |
| Chủ sở hữu governance | repo starter | tài liệu này |
| Reference | `$GOLD_RELEASE_DIR` (protected gold release) | reference riêng tư của pilot |

Ba luật cứng, gate G-05 kiểm tự động (`scripts/check-starter-alignment.py`):

1. Ảnh/nhãn cabin không bao giờ vào `dataset/images|labels` của starter.
2. Nhãn cabin không bao giờ là input fine-tune — luật `v=0` của Lane C mâu thuẫn với luật
   occluded-in-frame `v=1` của starter (D-01 trong `STARTER_ALIGNMENT.md`).
3. `$GOLD_RELEASE_DIR`, `$PROTECTED_SOURCE_DIR` và mọi mapping nguồn của baseline không bao giờ
   được sao vào repo pilot hay repo learner, kể cả trong lịch sử commit. Hai ký hiệu này định
   nghĩa ở `STARTER_ALIGNMENT.md` mục 1.

Lane S dùng 30 ảnh COCO val2017 (annotation CC BY 4.0; ảnh là ảnh Flickr do COCO phân phối theo
điều khoản riêng của COCO), lọc theo tiêu chí "người trong và quanh phương tiện", ngưỡng chiều
cao bbox 40%. **Không được nói đây là ảnh trong cabin** — nói rõ trong lớp rằng đó là proxy cho
hai hiện tượng cần dạy: tự che khuất cổ tay/hông, và khớp ra ngoài khung. Chi tiết provenance
nằm trong `$PROTECTED_SOURCE_DIR` của baseline và không phát ra ngoài.

## Active classroom lane (Lane C)

`data/images/` contains 10 derivatives from 10 distinct participant/recording codes across three public datasets. The pack uses consented human scans and real people, so no asset is described as anonymous. It is restricted to classroom/noncommercial use because the combined pack inherits the stricter CC BY-NC 4.0 boundary.

- HSRD-100: two front-view crops from two 3D scan previews under CC BY 4.0. Its dataset card records informed consent, removal of direct identifiers, redistribution rights and pose estimation as an intended use. The scans may still be recognizable; they are used only for guided COCO-17 calibration.
- Driver Risk Behavior Dataset: five real-vehicle frames under CC BY 4.0. The landing page says images were anonymised, but visual inspection found identifiable faces. The pilot therefore crops to the driver ROI, applies an opaque face mask and strips metadata before use.
- HADRIAN RGB/Depth directory: three simulator frames from three participant IDs under CC BY-NC 4.0. The publisher states faces were masked and participants without dissemination consent were excluded.
- Every output is re-encoded as RGB JPEG without EXIF, ICC or XMP; dimensions and SHA-256 are locked in `data/image-manifest.csv`.
- Source behaviour labels are provenance only. They are not copied into CVAT and are not treated as driver-state truth.

## Annotation boundary

Blur/mask đơn lẻ không tự động làm dữ liệu vô danh. On the two guided HSRD crops, all 17 nodes are observable and location-scored. On the eight cabin images, `nose`, `left_eye`, `right_eye`, `left_ear` and `right_ear` are unobservable by design: keep the nodes and mark them `Outside` (`v=0`); tọa độ bên dưới mask **không được đánh giá**. Lower-body points follow the actual crop; never infer a joint merely to complete the skeleton.

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
