# Third-party notices and sources

## Lane S — starter repo và dataset lớp học

- **Day4-TrackData-Keypoint-Pose** (VinUni-AI20k), commit `79f6724ec1f06cbb5a0dd81425f8a1594fcb8de3`:
  <https://github.com/VinUni-AI20k/Day4-TrackData-Keypoint-Pose>. Pilot dùng nguyên dataset,
  toolchain chấm, rubric, notebook và skeleton assets của repo này; không fork, không sao chép
  vào repo pilot. Ràng buộc và điểm lệch: `STARTER_ALIGNMENT.md`.
- **COCO val2017 person keypoints**, <https://cocodataset.org/#keypoints-2020>. Annotation
  CC BY 4.0; ảnh là ảnh Flickr do COCO phân phối theo điều khoản của COCO. Starter dùng 30/5000
  ảnh val, lọc theo tiêu chí "người trong và quanh phương tiện". Pilot chỉ đọc tại chỗ.
- **Ultralytics** (notebook của starter cài `-U`, không pin) và checkpoint pose tải lúc chạy:
  xem AGPL-3.0/Enterprise tại <https://www.ultralytics.com/license>. Không redistribute weight.

## Lane C — active image pack

- **HSRD-100: 100 High-Quality 3D Human Scans Dataset**, Digital Reality Lab, pinned revision `fe753f2eb34ec0194511eecebbcbffa2fddb67e1`, licensed CC BY 4.0: <https://huggingface.co/datasets/digitalrealitylab/HSRD-100>. Changes: selected two consented scan previews, cropped one front view/person, stripped metadata and re-encoded JPEG.
- **Driver Risk Behavior Dataset for Embedded Vision Applications**, Juan Manuel Calvo Duque, version 1, DOI `10.17632/562zj8n7xf.1`, licensed CC BY 4.0: <https://data.mendeley.com/datasets/562zj8n7xf/1>. Changes: selected five frames from five recording groups, cropped to driver ROI, applied opaque face masks, stripped metadata and re-encoded JPEG.
- **RGB and Depth videos directory**, Leandro L. Di Stasi et al., version 1, DOI `10.25452/figshare.plus.22277668.v1`, licensed CC BY-NC 4.0: <https://plus.figshare.com/articles/dataset/RGB_and_Depth_videos_directory/22277668>. Changes: selected three frames from three participant videos, preserved the publisher's face mask, applied documented sensor stressors, stripped metadata and re-encoded JPEG.
- The combined image pack is for classroom/noncommercial use. Attribution, licence links and indication of changes must travel with any copy. No endorsement by the source authors is implied.

Exact members, timestamps, source integrity values, transformations and output SHA-256 hashes are in `data/source-selection.json` and `data/image-manifest.csv`.

## Technical dependencies and references

- CVAT skeleton SVG/COCO Keypoints workflow: Apache-2.0 project and documentation at <https://github.com/cvat-ai/cvat> and <https://docs.cvat.ai/docs/manual/advanced/skeletons/>.
- COCO person keypoint names/topology: <https://cocodataset.org/#keypoints-2020>.
- Optional diagnostic: `ultralytics==8.4.145` and runtime-downloaded `yolo11n-pose.pt`; review AGPL-3.0/Enterprise terms at <https://www.ultralytics.com/license>. No weight is redistributed.
- DriPE, DMD and Drive&Act informed the coverage design but are not bundled or mirrored.

This notice records attribution and engineering boundaries; it is not legal advice.
