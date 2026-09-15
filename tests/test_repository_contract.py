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
    dimensions = {name: (640, 640) for name in PILOT_IMAGE_NAMES}
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
        cls.notebook_path = ROOT / "notebooks" / "day4_pose_finetune_yolo26.ipynb"
        cls.notebook = json.loads(cls.notebook_path.read_text(encoding="utf-8"))
        cls.code_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.notebook["cells"]
            if cell.get("cell_type") == "code"
        )

    def test_required_files_exist(self):
        expected = {
            "README.md",
            "STARTER_ALIGNMENT.md",
            "DATA_GOVERNANCE.md",
            "GUIDE.md",
            "lab-guide.html",
            "assets/guide/guide.css",
            "assets/guide/guide.js",
            "RUBRIC.md",
            "CVAT_TASK_SPEC.md",
            "PILOT_TEST_RUNBOOK.md",
            "REFERENCE_REVIEW_PROTOCOL.md",
            "PILOT_RUN_SHEET.md",
            "THIRD_PARTY_NOTICES.md",
            "day4_utils.py",
            "reports/POSE_REVIEW_TEMPLATE.md",
            "reports/VISIBILITY_REPORT_TEMPLATE.csv",
            "scripts/audit-data-pack.py",
            "scripts/check-starter-alignment.py",
            "scripts/convert_coco_to_yolo.py",
            "scripts/run-yolo11-diagnostic.py",
            "scripts/validate-submission.py",
            "tests/test_repository_contract.py",
        }
        missing = sorted(path for path in expected if not (ROOT / path).is_file())
        self.assertEqual(missing, [])

    def test_schedule_mirrors_the_starter_seven_stages(self):
        import re

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ranges = [tuple(map(int, match)) for match in re.findall(r"^\| (\d+)-(\d+) \|", readme, re.M)]
        self.assertEqual(len(ranges), 7)
        self.assertEqual(ranges[0], (0, 20))
        self.assertEqual(ranges[-1], (230, 240))
        self.assertEqual(sum(end - start for start, end in ranges), 240)
        self.assertTrue(all(left[1] == right[0] for left, right in zip(ranges, ranges[1:])))
        # Gold chỉ được phát sau khi nhãn đã khoá; chặng khoá nhãn phải kết thúc trước chặng gold.
        self.assertEqual(ranges[3][1], ranges[4][0])
        self.assertEqual(ranges[4][0], 150)

    def test_starter_alignment_contract_is_stated(self):
        alignment = (ROOT / "STARTER_ALIGNMENT.md").read_text(encoding="utf-8")
        self.assertIn("Day4-TrackData-Keypoint-Pose", alignment)
        for divergence in ("D-02", "D-03", "D-04", "D-05", "D-06", "D-07", "D-08"):
            self.assertIn(divergence, alignment)
        for gate in ("G-01", "G-02", "G-03", "G-04", "G-05", "G-06"):
            self.assertIn(gate, alignment)

        runbook = (ROOT / "PILOT_TEST_RUNBOOK.md").read_text(encoding="utf-8")
        run_sheet = (ROOT / "PILOT_RUN_SHEET.md").read_text(encoding="utf-8")
        for gate in ("G-01", "G-02", "G-03", "G-04", "G-05", "G-06"):
            self.assertIn(gate, runbook, f"{gate} không có cách chạy trong runbook")
            self.assertIn(gate, run_sheet, f"{gate} không có chỗ ghi kết quả trong run sheet")

        checker = ROOT / "scripts" / "check-starter-alignment.py"
        ast.parse(checker.read_text(encoding="utf-8"))
        result = subprocess.run(
            [sys.executable, str(checker), "--starter", str(ROOT / "does-not-exist")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0, "checker phải fail khi không thấy starter")

    def test_data_pack_matches_manifest_and_has_no_metadata(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit-data-pack.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_schema_json_and_svg_match_coco17(self):
        svg_file = ROOT / "assets/schema/coco17-cvat-skeleton.svg"
        if svg_file.is_file():
            svg_root = ET.parse(svg_file).getroot()
            namespace = "{http://www.w3.org/2000/svg}"
            circles = svg_root.findall(f"{namespace}circle")
            lines = svg_root.findall(f"{namespace}line")
            self.assertEqual(len(circles), 17)
            self.assertEqual(len(lines), 19)
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
        self.assertTrue(all(cell.get("execution_count") is None and cell.get("outputs", []) == [] for cell in code_cells))
        clean_code = "\n".join(
            line for line in self.code_source.splitlines() if not line.strip().startswith(("%", "!"))
        )
        ast.parse(clean_code)

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
        self.assertIn("pilot-v0.4", documents)
        self.assertNotIn("pilot-v0.3", documents)
        self.assertIn("ultralytics==8.4.145", documents)

    def test_lane_boundary_is_stated_where_the_cabin_pack_is_described(self):
        for name, marker in (
            ("DATA_GOVERNANCE.md", "Active classroom dataset"),
            ("REFERENCE_REVIEW_PROTOCOL.md", "$GOLD_RELEASE_DIR"),
            ("THIRD_PARTY_NOTICES.md", "COCO val2017"),
        ):
            document = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(marker, document, f"{name} thiếu ranh giới")


    def test_authority_model_keeps_lab_decisions_with_the_owner(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        alignment = (ROOT / "STARTER_ALIGNMENT.md").read_text(encoding="utf-8")
        for document, name in ((readme, "README.md"), (alignment, "STARTER_ALIGNMENT.md")):
            self.assertIn("technical compatibility baseline", document, name)
        # Starter chỉ là baseline kỹ thuật; timeline/objective/rubric/release thuộc owner pilot.
        self.assertIn("owner pilot", alignment)
        for decision in ("Timeline", "Learning objective", "Rubric", "freeze/release"):
            self.assertIn(decision, alignment, f"{decision} phải có chủ sở hữu rõ ràng")
        self.assertIn("pilot-v0.4-alpha", readme)
        self.assertIn("pilot-v0.4-alpha", alignment)
        self.assertIn("pilot-v0.4-alpha", (ROOT / "PILOT_RUN_SHEET.md").read_text(encoding="utf-8"))
        for document, name in ((readme, "README.md"), (alignment, "STARTER_ALIGNMENT.md")):
            self.assertNotIn("source of truth", document.casefold(), name)
            self.assertNotIn("nguồn chân lý", document, name)

    def repository_text_files(self):
        skipped = {".git", "outputs", "assets", "scratch"}
        suffixes = {".md", ".py", ".html", ".css", ".js", ".json", ".csv", ".txt"}
        for path in sorted(ROOT.rglob("*")):
            relative = path.relative_to(ROOT)
            if not path.is_file() or path.suffix not in suffixes:
                continue
            if skipped.intersection(relative.parts):
                continue
            yield relative, path.read_text(encoding="utf-8", errors="replace")

    def test_no_role_wording_in_tracked_documents_or_scripts(self):
        # Đường dẫn theo vai trò bị cấm; dùng ký hiệu trung tính trong STARTER_ALIGNMENT.md mục 1.
        # Ghép chuỗi để chính file test này không tự vi phạm luật nó đang kiểm.
        role = "instr" + "uctor"
        teacher = "giảng " + "viên"
        forbidden = (role + "/", role + "\\", teacher, teacher.capitalize())
        offenders = [
            f"{relative}: {term}"
            for relative, text in self.repository_text_files()
            for term in forbidden
            if term in text
        ]
        self.assertEqual(offenders, [])

    def test_starter_commit_pin_is_consistent_and_enforced(self):
        checker_source = (ROOT / "scripts" / "check-starter-alignment.py").read_text(encoding="utf-8")
        tree = ast.parse(checker_source)
        pins = [
            node.value.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "PINNED_STARTER_COMMIT"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
        ]
        self.assertEqual(len(pins), 1, "checker phải pin đúng một commit")
        pin = pins[0]
        self.assertEqual(len(pin), 40)
        self.assertIn("--allow-unpinned", checker_source, "phải có lối thoát tường minh khỏi pin")
        for name in (
            "README.md",
            "STARTER_ALIGNMENT.md",
            "PILOT_RUN_SHEET.md",
            "PILOT_TEST_RUNBOOK.md",
        ):
            self.assertIn(pin, (ROOT / name).read_text(encoding="utf-8"), f"{name} pin lệch commit")

    def test_checker_verifies_the_evaluator_and_skeleton_assets(self):
        checker_source = (ROOT / "scripts" / "check-starter-alignment.py").read_text(encoding="utf-8")
        for marker in (
            "evaluate_pose_annotations.py",
            "labels_day4.json",
            "skeleton_person_17.svg",
            "skeleton_hand_21.svg",
            "skeleton_face_5.svg",
            "dao_trai_phai",
            "nham_nguoi",
            "xoa_khop_bi_che",
        ):
            self.assertIn(marker, checker_source, f"G-05 chưa kiểm {marker}")

    def test_lane_s_is_documented_as_two_cvat_tasks(self):
        spec = (ROOT / "CVAT_TASK_SPEC.md").read_text(encoding="utf-8")
        runbook = (ROOT / "PILOT_TEST_RUNBOOK.md").read_text(encoding="utf-8")
        run_sheet = (ROOT / "PILOT_RUN_SHEET.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("task CVAT thứ hai", spec)
        self.assertIn("annotations/face_hand/", spec)
        self.assertIn("task CVAT thứ hai", runbook)
        for document, name in (
            (spec, "CVAT_TASK_SPEC.md"),
            (runbook, "PILOT_TEST_RUNBOOK.md"),
            (run_sheet, "PILOT_RUN_SHEET.md"),
            (readme, "README.md"),
        ):
            folded = document.casefold()
            self.assertIn("task a", folded, f"{name} thiếu task A")
            self.assertIn("task b", folded, f"{name} thiếu task B")

    def test_scope_changes_are_owner_decisions_not_runbook_fallbacks(self):
        runbook = (ROOT / "PILOT_TEST_RUNBOOK.md").read_text(encoding="utf-8")
        run_sheet = (ROOT / "PILOT_RUN_SHEET.md").read_text(encoding="utf-8")
        self.assertIn("Decisions pending owner", runbook)
        self.assertIn("Decisions pending owner", run_sheet)
        for identifier in ("DP-1", "DP-2", "DP-3", "DP-4"):
            self.assertIn(identifier, run_sheet)
        # T-10 chỉ ghi bằng chứng; cắt face/hand hay giảm epoch không được tự kích hoạt.
        flowed = " ".join(runbook.split())
        self.assertIn("Runbook **không** có fallback tự động", flowed)
        self.assertNotIn("Ưu tiên cắt bộ face/hand", flowed)
        self.assertNotIn("đề xuất giảm epoch cho lớp", flowed)

    def test_html_guide_covers_the_active_pack(self):
        guide = (ROOT / "lab-guide.html").read_text(encoding="utf-8")
        flowed = " ".join(guide.split())
        self.assertIn('lang="vi"', guide)
        self.assertIn('href="#main-content"', guide)
        self.assertIn("COCO-17", guide)
        self.assertIn("HƯỚNG DẪN HỌC VIÊN", guide)
        self.assertNotIn("TÀI LIỆU NỘI BỘ", flowed)
        self.assertIn("repo starter", guide)
        self.assertIn("COCO Keypoints 1.0", guide)

        # On-ramp cho học viên nontech: lệnh sao chép được, link CVAT chung, bảng thuật ngữ.
        self.assertIn("data-copy=", guide)
        self.assertIn("http://localhost:8080", guide)
        self.assertNotIn("localhost:8080/tasks/", guide)
        self.assertIn('id="glossary"', guide)

        # Phóng to ảnh phải mở lightbox trong trang, không điều hướng ra file ảnh.
        self.assertIn("data-lightbox", guide)
        self.assertIn('aria-modal="true"', guide)
        self.assertIn("data-lightbox-close", guide)
        self.assertNotIn('target="_blank"', guide)

        cvat_dir = ROOT / "assets" / "guide" / "cvat"
        for screenshot_name in (
            "01-job-overview.jpg",
            "02-select-skeleton.jpg",
            "03-export-menu.jpg",
            "04-toolbar-top.jpg",
            "05-labels-panel.jpg",
            "06-draw-skeleton.jpg",
            "07-export-menu-detail.jpg",
            "08-menu-save.jpg",
        ):
            self.assertTrue((cvat_dir / screenshot_name).is_file())
        # Sáu thao tác phải kèm ảnh CVAT thật, không chỉ chữ.
        workflow = guide.split('id="workflow"', 1)[1].split("</section>", 1)[0]
        for screenshot_name in (
            "08-menu-save.jpg",
            "05-labels-panel.jpg",
            "06-draw-skeleton.jpg",
            "07-export-menu-detail.jpg",
        ):
            self.assertIn(screenshot_name, workflow)


class CocoKeypointsValidatorTest(unittest.TestCase):
    def test_valid_archive_and_visibility_counts(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = write_coco_zip(Path(temporary) / "valid.zip")
            report = audit_coco_keypoints_archive(archive)
        self.assertEqual(report["image_count"], 20)
        self.assertEqual(report["annotation_count"], 20)
        self.assertTrue(report["semantic_review_required"])
        left_wrist = report["visibility_rows"][9]
        self.assertEqual(left_wrist["v1_occluded"], 1)
        self.assertEqual(left_wrist["v2_visible"], 19)
        left_ankle = report["visibility_rows"][15]
        self.assertEqual(left_ankle["v0_outside_or_unlabeled"], 18)
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
