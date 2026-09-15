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



## Technical dependencies and references

- CVAT skeleton SVG/COCO Keypoints workflow: Apache-2.0 project and documentation at <https://github.com/cvat-ai/cvat> and <https://docs.cvat.ai/docs/manual/advanced/skeletons/>.
- COCO person keypoint names/topology: <https://cocodataset.org/#keypoints-2020>.
- Optional diagnostic: `ultralytics==8.4.145` and runtime-downloaded `yolo11n-pose.pt`; review AGPL-3.0/Enterprise terms at <https://www.ultralytics.com/license>. No weight is redistributed.
- DriPE, DMD and Drive&Act informed the coverage design but are not bundled or mirrored.

This notice records attribution and engineering boundaries; it is not legal advice.
