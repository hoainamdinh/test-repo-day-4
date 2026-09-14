# CVAT Docker → COCO Keypoints POC

Run date: 2026-09-14. Environment: the pre-existing local CVAT Docker stack at `http://localhost:8080`, CVAT v2.74.1. No new container or service was started.

## Scope and result

- Created task `DAY04-POSE-PILOT-V01` (task #14, job #10) with the two pilot PNGs.
- Imported `data/schema/coco17-cvat-skeleton.svg` as one `person` skeleton with 17 ordered sublabels.
- Saved one skeleton per image and exercised all visibility states: visible, right wrist occluded, and both ankles outside on the cropped image.
- Exported job annotations as **COCO Keypoints 1.0**, without images.
- Ran the repository validator on the unedited CVAT ZIP. Result: **PASS structural audit** with 2 images, 2 annotations, 17 keypoints and the expected `v=0/1/2` counts.
- Re-import was not run because it is not part of the learner submission path. It remains a conditional classroom check if the deployed course workflow later depends on import.

This is a structural interoperability POC, not a semantic reference annotation. The point placements used to exercise the format must not be distributed as an answer key.

## Evidence

Artifacts are kept under ignored `outputs/cvat-poc/` so the repository contract does not accidentally publish annotations.

| Artifact | SHA-256 | Finding |
| --- | --- | --- |
| `COCO_KEYPOINTS_EXPORT.zip` | `15b35bb38bb56246aadf7cfdc454afaad92ccddcf035059fc074309b9ecefdbe` | validator PASS |
| `VISIBILITY_REPORT.csv` | `373ae76686e3d32fbf688d50646fbe9c22524caa61cb590f73b897e46bb08d5e` | right wrist has one `v=1`; each ankle has one `v=0` |
| `COCO_KEYPOINTS_EXPORT-before-geometry-fix.zip` | `e0ece801a7a5c83a3cc6820acd7076cda364c21840469129b8071f02bcce8736` | validator correctly rejected zero-width bbox |

The passing archive contains exactly `annotations/person_keypoints_default.json`.

## Defects found and fixed

1. CVAT rejected the first SVG with `Wrong skeleton structure`. The v2.74.1 importer requires an SVG `<desc data-description-type="labels-specification">` payload in addition to nodes and edges. The reusable SVG and its repository test now enforce that contract.
2. A drag gesture created a zero-width skeleton on frame 0. The first real export failed the validator with `bbox width/height phải dương`. After fixing the geometry in CVAT and saving, a new unedited export passed. This confirms the validator detects a concrete authoring defect rather than accepting any CVAT-produced ZIP.

## Remaining release gates

- Smoke-test the same SVG/export contract on the authenticated classroom deployment.
- Run the two-person semantic reference review outside the repository.
- Expand to 2 guided + 8 independent images and complete the timed 240-minute dry-run.
- This historical two-image POC does not freeze the current evidence-ladder pack. Re-run the smoke test with all 10 v0.3 images before freezing `pilot-v0.3`.
