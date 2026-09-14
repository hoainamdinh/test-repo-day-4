# YOLO11 diagnostic POC

Run date: 2026-09-14. Runtime: local macOS, Python 3.13, `ultralytics==8.4.145`, `yolo11n-pose.pt` downloaded from the Ultralytics v8.4 asset release.

Command:

```bash
python3 scripts/run-yolo11-diagnostic.py --acknowledge-license-review
```

Result: exit 0 on both pilot images. Output overlays were written under ignored `outputs/yolo11-diagnostic/`. The downloaded weight was removed after the run and is not part of the pilot repository.

Visual finding: the model found one person with high confidence in each image, but inferred lower-body joints at/near the crop boundary even where ankles were not visible. This is useful evidence for the teaching order: learner attempt and self-QC first; model output later as a fallible diagnostic, never as reference.

This POC proves runtime compatibility only. It does not validate CVAT export semantics, annotation accuracy or enterprise license suitability.
