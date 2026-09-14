# Day 4 pilot run sheet

## Run metadata

- Date/time: 2026-09-14 (local technical POC)
- Lab Coach: pending human run
- CVAT URL/version/build: local Docker `http://localhost:8080`, CVAT v2.74.1
- Browser/OS: Codex in-app browser / macOS
- Image manifest SHA-256: `5c729b2ef55fc52a72cb2ba4853a942e1e32958dd4e03436dffaedfb584becd0`
- Schema JSON SHA-256: `db7e27f8e716bf3f1724aeb325a57ce876347b598ea6df00cb1548dfd76a950a`
- Skeleton SVG SHA-256: `7c67a45fe59d16a1f4adcff791e9279d6be6f884c05b91017da168c8669b64df`

## Technical POC

| Check | Evidence path/hash | Result | Notes |
| --- | --- | --- | --- |
| SVG import and 17 ordered sublabels | task #14/job #10 | pass | importer contract includes labels-specification `<desc>` |
| Save/reload skeleton | task #14/job #10 | pass | 2 parent skeletons + 34 element shapes persisted |
| Visible → `v=2` | `VISIBILITY_REPORT.csv` | pass | visible counts present for all keypoints |
| Occluded → `v=1` | right_wrist row | pass | one occluded right wrist |
| Outside → `v=0` | ankle rows | pass | one outside value for each ankle |
| COCO Keypoints export audit | ZIP SHA `15b35b...fdbe` | pass | unedited CVAT export; 2 images/2 annotations |
| Visibility CSV reconciliation | CSV SHA `373ae7...8d5e` | pass | expected counts match UI states |
| Re-import when required | — | not applicable | learner submission path does not import; retain conditional classroom check |

Full evidence and the defect/fix trace are in `POC_CVAT_COCO_ROUNDTRIP.md`. The local Docker deployment is the canonical pilot target; the previously visited hosted instance is out of scope and is not used as release evidence.

## v0.3 local Docker smoke

| Check | Evidence | Result | Notes |
| --- | --- | --- | --- |
| Final task creation | task #16/job #12 | pass | local Docker CVAT v2.74.1; 10 frames, range 0-9 |
| `person` skeleton import | task #16 | pass | edit view shows all 17 ordered COCO sublabels |
| Evidence-ladder order | job #12, frames 0-2 | pass | two calibration images first; cabin images begin at frame 2 |
| Save/reload visibility semantics | — | pending | annotate representative calibration and cabin frames before freeze |
| v0.3 COCO export/validator round-trip | — | pending | required before `pilot-v0.3` release decision |

## Timed run

| Participant route | A | B | C | D | E | F | Finish | Support requests | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| novice/non-tech | | | | | | | | | pending |
| experienced | | | | | | | | | pending |

## Release decision

- Lab Coach test handoff: `ready`
- Freeze/student release: `hold`
- Blocking findings: v0.3 semantic save/reload/export round-trip; novice and experienced 240-minute dry-runs
- Changes made and retested:
- Private reference location confirmed:
- Instructor handoff PR/link:
- Lab Coach sign-off:
