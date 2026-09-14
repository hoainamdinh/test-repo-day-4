import ast
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from day4_utils import (  # noqa: E402
    COCO_SKELETON,
    EXPECTED_SUBMISSION_FILES,
    KEYPOINT_NAMES,
    PILOT_IMAGE_NAMES,
    ValidationError,
    audit_coco_keypoints_archive,
    validate_submission_directory,
    write_visibility_report,
)


def build_valid_coco():
    with (ROOT / "data" / "image-manifest.csv").open(encoding="utf-8", newline="") as source:
        manifest_rows = list(csv.DictReader(source))
    dimensions = {
        row["filename"]: (int(row["width"]), int(row["height"])) for row in manifest_rows
    }
    images = [
        {
            "id": index,
            "file_name": name,
            "width": dimensions[name][0],
            "height": dimensions[name][1],
        }
        for index, name in enumerate(PILOT_IMAGE_NAMES, start=1)
    ]
    annotations = []
    for image in images:
        keypoints = []
        for index, _name in enumerate(KEYPOINT_NAMES):
            visibility = 2
            if image["id"] == 1 and index == 9:
                visibility = 1
            if image["id"] >= 3 and index in {0, 1, 2, 3, 4, 13, 14, 15, 16}:
                visibility = 0
            x, y = (0, 0) if visibility == 0 else (60 + index * 10, 80 + index * 5)
            keypoints.extend((x, y, visibility))
        annotations.append(
            {
                "id": image["id"],
                "image_id": image["id"],
                "category_id": 1,
                "bbox": [40, 60, 300, 350],
                "area": 105000,
                "iscrowd": 0,
                "keypoints": keypoints,
                "num_keypoints": sum(keypoints[index] > 0 for index in range(2, 51, 3)),
            }
        )
    return {
        "images": images,
        "annotations": annotations,
        "categories": [
            {
                "id": 1,
                "name": "person",
                "supercategory": "person",
                "keypoints": list(KEYPOINT_NAMES),
                "skeleton": [list(edge) for edge in COCO_SKELETON],
            }
        ],
    }


def write_coco_zip(path: Path, payload=None, member="annotations/person_keypoints_default.json"):
    payload = payload or build_valid_coco()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, json.dumps(payload))
    return path


class RepositoryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook_path = ROOT / "notebooks" / "day4-pose-quality.ipynb"
        cls.notebook = json.loads(cls.notebook_path.read_text(encoding="utf-8"))
        cls.code_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.notebook["cells"]
            if cell.get("cell_type") == "code"
        )

    def test_required_files_exist(self):
        expected = {
            "README.md",
            "DATA_GOVERNANCE.md",
            "GUIDE.md",
            "lab-guide.html",
            "assets/guide/guide.css",
            "assets/guide/guide.js",
            "RUBRIC.md",
            "CVAT_TASK_SPEC.md",
            "PILOT_TEST_RUNBOOK.md",
            "MODEL_DIAGNOSTIC_POC.md",
            "POC_CVAT_COCO_ROUNDTRIP.md",
            "REFERENCE_REVIEW_PROTOCOL.md",
            "PILOT_RUN_SHEET.md",
            "THIRD_PARTY_NOTICES.md",
            "day4_utils.py",
            "data/README.md",
            "data/GENERATION_RECORD.md",
            "data/image-manifest.csv",
            "data/schema/coco17-keypoints.json",
            "data/schema/coco17-cvat-skeleton.svg",
            "notebooks/day4-pose-quality.ipynb",
            "reports/POSE_REVIEW_TEMPLATE.md",
            "reports/VISIBILITY_REPORT_TEMPLATE.csv",
            "scripts/audit-data-pack.py",
            "scripts/build-notebook.py",
            "scripts/run-yolo11-diagnostic.py",
            "scripts/validate-submission.py",
            "tests/test_repository_contract.py",
        }
        missing = sorted(path for path in expected if not (ROOT / path).is_file())
        self.assertEqual(missing, [])

    def test_schedule_is_contiguous_and_240_minutes(self):
        import re

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ranges = [tuple(map(int, match)) for match in re.findall(r"^\| (\d+)-(\d+) \|", readme, re.M)]
        self.assertEqual(ranges[0], (0, 15))
        self.assertEqual(ranges[-1], (237, 240))
        self.assertEqual(sum(end - start for start, end in ranges), 240)
        self.assertTrue(all(left[1] == right[0] for left, right in zip(ranges, ranges[1:])))

    def test_data_pack_matches_manifest_and_has_no_metadata(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit-data-pack.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with (ROOT / "data" / "image-manifest.csv").open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["participant_code"] for row in rows}), 10)
        self.assertEqual(sum(row["role"] == "guided" for row in rows), 2)
        self.assertEqual(sum(row["role"] == "independent" for row in rows), 8)
        self.assertEqual(
            {row["source_type"] for row in rows},
            {"public-real-derived", "public-consented-scan-derived"},
        )
        self.assertEqual(len({row["source_dataset"] for row in rows}), 3)
        self.assertEqual(
            [row["facial_keypoints_scored"] for row in rows].count("yes"), 2
        )
        self.assertEqual(
            [row["facial_keypoints_scored"] for row in rows].count("no"), 8
        )
        for row in rows:
            image = ROOT / "data" / "images" / row["filename"]
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), row["sha256"])

    def test_schema_json_and_svg_match_coco17(self):
        schema = json.loads((ROOT / "data/schema/coco17-keypoints.json").read_text(encoding="utf-8"))
        self.assertEqual(tuple(schema["keypoints"]), KEYPOINT_NAMES)
        self.assertEqual(tuple(tuple(edge) for edge in schema["skeleton"]), COCO_SKELETON)
        self.assertEqual(schema["flip_idx"], [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15])

        svg_root = ET.parse(ROOT / "data/schema/coco17-cvat-skeleton.svg").getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        circles = svg_root.findall(f"{namespace}circle")
        lines = svg_root.findall(f"{namespace}line")
        self.assertEqual([circle.attrib["data-label-name"] for circle in circles], list(KEYPOINT_NAMES))
        self.assertEqual(len({circle.attrib["data-node-id"] for circle in circles}), 17)
        self.assertTrue(all(circle.attrib["data-type"] == "element node" for circle in circles))
        self.assertEqual(len(lines), 19)
        self.assertTrue(all(line.attrib["data-type"] == "edge" for line in lines))
        descriptions = svg_root.findall(f"{namespace}desc")
        self.assertEqual(len(descriptions), 1)
        self.assertEqual(descriptions[0].attrib["data-description-type"], "labels-specification")
        label_spec = json.loads(descriptions[0].text)
        self.assertEqual([label_spec[str(index)]["name"] for index in range(1, 18)], list(KEYPOINT_NAMES))

    def test_notebook_is_clean_parseable_and_reproducible(self):
        self.assertEqual(self.notebook["nbformat"], 4)
        code_cells = [cell for cell in self.notebook["cells"] if cell["cell_type"] == "code"]
        self.assertTrue(all(cell["execution_count"] is None and cell["outputs"] == [] for cell in code_cells))
        ast.parse(self.code_source)
        before = self.notebook_path.read_bytes()
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build-notebook.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(before, self.notebook_path.read_bytes())
        self.assertNotIn("%pip", self.code_source)
        self.assertNotIn("ultralytics", self.code_source.casefold())

    def test_private_reference_and_weights_are_not_bundled(self):
        self.assertEqual(list(ROOT.rglob("*.pt")), [])
        self.assertEqual(list(ROOT.rglob("*reference*.json")), [])
        self.assertEqual(list(ROOT.rglob("*reference*.zip")), [])
        governance = (ROOT / "DATA_GOVERNANCE.md").read_text(encoding="utf-8")
        self.assertIn("Blur/mask đơn lẻ không tự động", governance)
        self.assertIn("không được đánh giá", governance)

    def test_pilot_contract_and_model_order_are_explicit(self):
        documents = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("README.md", "GUIDE.md", "PILOT_TEST_RUNBOOK.md")
        )
        self.assertIn("Chỉ freeze", documents)
        self.assertIn("240 phút", documents)
        self.assertIn("independent attempt", documents)
        self.assertIn("sau self-QC", documents)
        self.assertIn("pilot-v0.3", documents)
        self.assertIn("ultralytics==8.4.145", documents)

    def test_html_guide_covers_the_active_pack(self):
        guide = (ROOT / "lab-guide.html").read_text(encoding="utf-8")
        self.assertIn('lang="vi"', guide)
        self.assertIn('href="#main-content"', guide)
        self.assertIn("COCO-17", guide)
        self.assertIn("240 PHÚT", guide)
        self.assertIn("PILOT_TEST_RUNBOOK.md", guide)
        self.assertIn("Làm theo ảnh, rồi kiểm ngay trên task.", guide)
        self.assertIn("COCO Keypoints 1.0", guide)
        for image_name in PILOT_IMAGE_NAMES:
            self.assertIn(image_name, guide)
        for screenshot_name in (
            "01-job-overview.png",
            "02-select-skeleton.png",
            "03-export-menu.png",
        ):
            self.assertIn(screenshot_name, guide)
            self.assertTrue((ROOT / "assets" / "guide" / "cvat" / screenshot_name).is_file())


class CocoKeypointsValidatorTest(unittest.TestCase):
    def test_valid_archive_and_visibility_counts(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "valid.zip")
            report = audit_coco_keypoints_archive(archive)
        self.assertEqual(report["image_count"], 10)
        self.assertEqual(report["annotation_count"], 10)
        self.assertTrue(report["semantic_review_required"])
        left_wrist = report["visibility_rows"][9]
        self.assertEqual(left_wrist["v1_occluded"], 1)
        self.assertEqual(left_wrist["v2_visible"], 9)
        left_ankle = report["visibility_rows"][15]
        self.assertEqual(left_ankle["v0_outside_or_unlabeled"], 8)
        self.assertEqual(left_ankle["v2_visible"], 2)

    def test_rejects_unsafe_zip_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "unsafe.zip", member="../person_keypoints.json")
            with self.assertRaisesRegex(ValidationError, "không an toàn"):
                audit_coco_keypoints_archive(archive)

    def test_rejects_wrong_keypoint_order(self):
        payload = build_valid_coco()
        payload["categories"][0]["keypoints"][1:3] = reversed(payload["categories"][0]["keypoints"][1:3])
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "wrong-schema.zip", payload)
            with self.assertRaisesRegex(ValidationError, "sai tên hoặc thứ tự"):
                audit_coco_keypoints_archive(archive)

    def test_accepts_equivalent_skeleton_edge_order(self):
        payload = build_valid_coco()
        payload["categories"][0]["skeleton"] = [
            list(reversed(edge)) for edge in reversed(payload["categories"][0]["skeleton"])
        ]
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "edge-order.zip", payload)
            report = audit_coco_keypoints_archive(archive)
        self.assertEqual(report["keypoint_count"], 17)

    def test_rejects_non_integer_image_id_cleanly(self):
        payload = build_valid_coco()
        payload["images"][0]["id"] = [1]
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "bad-id.zip", payload)
            with self.assertRaisesRegex(ValidationError, "integer >= 1"):
                audit_coco_keypoints_archive(archive)

    def test_rejects_num_keypoints_mismatch(self):
        payload = build_valid_coco()
        payload["annotations"][0]["num_keypoints"] = 16
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "bad-count.zip", payload)
            with self.assertRaisesRegex(ValidationError, r"count\(v>0\)"):
                audit_coco_keypoints_archive(archive)

    def test_rejects_wrong_image_pack(self):
        payload = build_valid_coco()
        payload["images"][0]["file_name"] = "other.png"
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "wrong-image.zip", payload)
            with self.assertRaisesRegex(ValidationError, "Image basename mismatch"):
                audit_coco_keypoints_archive(archive)

    def test_complete_submission_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            export = write_coco_zip(directory / "COCO_KEYPOINTS_EXPORT.zip")
            report = audit_coco_keypoints_archive(export)
            write_visibility_report(report, directory / "VISIBILITY_REPORT.csv")
            review = "\n".join(
                [
                    "# Pose review",
                    "SELF_QC_COMPLETE: yes",
                    "PEER_REVIEW_COMPLETE: yes",
                    "REWORK_COMPLETE: yes",
                    *PILOT_IMAGE_NAMES,
                    "Evidence complete.",
                ]
            )
            (directory / "POSE_REVIEW.md").write_text(review, encoding="utf-8")
            result = validate_submission_directory(directory)
        self.assertEqual(set(result["files"]), EXPECTED_SUBMISSION_FILES)
        self.assertTrue(result["structural_pass"])

    def test_submission_rejects_stale_visibility_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            write_coco_zip(directory / "COCO_KEYPOINTS_EXPORT.zip")
            (directory / "VISIBILITY_REPORT.csv").write_text(
                "keypoint_index,keypoint_name,v0_outside_or_unlabeled,v1_occluded,v2_visible,total\n",
                encoding="utf-8",
            )
            (directory / "POSE_REVIEW.md").write_text(
                "SELF_QC_COMPLETE: yes\nPEER_REVIEW_COMPLETE: yes\nREWORK_COMPLETE: yes\n"
                + "\n".join(PILOT_IMAGE_NAMES),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValidationError, "không khớp"):
                validate_submission_directory(directory)


if __name__ == "__main__":
    unittest.main()
