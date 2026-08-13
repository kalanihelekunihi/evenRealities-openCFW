#!/usr/bin/env python3
"""Qualify the recovered G2 NemaGFX/NemaVG and Ambiq GPU boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_nemagfx_ambiq_provenance.py"
MANIFEST = ROOT / "tools" / "manifests" / "g2-nemagfx-ambiq-provenance.json"
AVAILABLE_SDK = Path(
    "/Users/kalani/Repo/evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5"
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_nemagfx_ambiq_provenance", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NemaGFXAmbiqProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer.IMAGE.read_bytes()
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.report = cls.analyzer.audit(cls.data, cls.manifest)

    def test_public_commits_tree_and_versions_are_pinned(self) -> None:
        identity = self.report["dependency_identity"]
        self.assertEqual(
            identity["public_reproduction_commit"],
            "b853fded7e545f005727e13bf2ce83018c7e242d",
        )
        self.assertEqual(
            identity["public_subtree_git_tree_sha1"],
            "e690768a6e7b4d6a8d526fc75e8278a2764deff3",
        )
        self.assertEqual(
            identity["apollo5_archive_first_commit"],
            "c6f54a9587fcdc3cd10a9af5db0b602f34d5304f",
        )
        self.assertEqual(
            identity["gpu_patch_first_commit"],
            "e3eec7f3c1148fee3dfa33ca861be176de66c584",
        )
        self.assertEqual(identity["ambiqsuite_version"], "5.1.0")
        self.assertEqual(identity["ambiqsuite_revision"], "release_sdk5p1p0-634f7c117b")
        self.assertEqual(identity["nemagfx_version"]["semantic_version"], "1.4.12")
        self.assertEqual(identity["nemavg_version"]["semantic_version"], "1.1.8")
        self.assertIn("lower bound", identity["nemagfx_version"]["stock_resolution"])
        self.assertIn("not independently", identity["nemavg_version"]["stock_resolution"])

    def test_stock_configuration_and_version_discriminator_are_exact(self) -> None:
        config = self.report["stock_configuration"]
        self.assertEqual(config["LV_USE_DRAW_AMBIQ"], 1)
        self.assertEqual(config["LV_USE_AMBIQ_VG"], 1)
        self.assertEqual(config["LV_AMBIQ_COMMAND_LIST_SECTOR"], 100)
        self.assertEqual(config["LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE"], 1024)
        self.assertEqual(config["command_list_bytes"], 102400)
        self.assertEqual(config["NEMAGFX_POWER_SAVE"], 1)
        self.assertTrue(config["power_wake_retain_state"])
        retained = {item["run"]: item["text"] for item in self.report["retained_strings"]}
        self.assertEqual(retained[0x76C8E8], "INVALID_SECTORED_CL_SIZE")
        self.assertEqual(retained[0x76C920], "Power control failed: %d\r\n")

    def test_stock_nema_and_gpu_extension_spans_are_pinned(self) -> None:
        spans = self.report["pinned_spans"]
        self.assertEqual(len(spans), 11)
        self.assertEqual(spans["lv_ambiq_common_start"]["size"], 560)
        self.assertEqual(spans["lv_draw_ambiq_init"]["size"], 280)
        self.assertEqual(spans["nema_cl_create_sized"]["size"], 118)
        self.assertEqual(spans["nema_cl_bind_sectored_circular"]["size"], 230)
        self.assertEqual(spans["lv_ambiq_gradient_create"]["size"], 1416)
        self.assertEqual(spans["lv_ambiq_dashline_create"]["size"], 138)
        self.assertEqual(len(self.report["retained_paths"]), 2)

    def test_gpu_patch_export_and_required_api_censuses_are_closed(self) -> None:
        patch = self.report["gpu_patch"]
        exports = set(patch["exported_functions"])
        required = set(patch["functions_required_by_recovered_lvgl_subtree"])
        self.assertEqual(len(exports), 11)
        self.assertEqual(len(required), 6)
        self.assertLessEqual(required, exports)
        self.assertIn("lv_ambiq_gradient_create", required)
        self.assertIn("lv_ambiq_shadow_blur_corner", required)
        self.assertIn("binary archive only", patch["source_availability"])

    def test_complete_gpu_patch_function_section_census_is_pinned(self) -> None:
        census = self.report["gpu_patch"]["binary_recovery"]["function_census"]
        self.assertEqual(len(census), 11)
        self.assertEqual({item["function"] for item in census}, set(self.report["gpu_patch"]["exported_functions"]))
        self.assertEqual(sum(item["section_size"] for item in census), 4_232)
        self.assertEqual(sum(item["symbol_size"] for item in census), 4_230)
        self.assertEqual(sum(item["relocation_count"] for item in census), 138)
        bounded = [item for item in census if item["source_status"] == "bounded-clean-room-candidate"]
        binary_only = [item for item in census if item["source_status"] == "exact-binary-only"]
        self.assertEqual((len(bounded), sum(item["section_size"] for item in bounded)), (11, 4_232))
        self.assertEqual((len(binary_only), sum(item["section_size"] for item in binary_only)), (0, 0))
        self.assertEqual(
            next(item for item in census if item["function"] == "lv_ambiq_gradient_create")["source_line"],
            138,
        )

    def test_image_and_manifest_mutations_are_rejected(self) -> None:
        mutated_image = bytearray(self.data)
        mutated_image[
            self.analyzer.PINNED_SPANS["nema_cl_bind_sectored_circular"][0]
            - self.analyzer.LOAD_BASE
        ] ^= 1
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit(bytes(mutated_image), self.manifest)

        for mutation in ("archive", "patch", "config"):
            changed = copy.deepcopy(self.manifest)
            if mutation == "archive":
                changed["selected_artifacts"][5]["sha256"] = "0" * 64
            elif mutation == "patch":
                changed["gpu_patch"]["exported_functions"].pop()
            else:
                changed["stock_evidence"]["recovered_configuration"][
                    "LV_AMBIQ_COMMAND_LIST_SECTOR"
                ] = 99
            with self.subTest(mutation=mutation), self.assertRaises(
                self.analyzer.AuditError
            ):
                self.analyzer.audit(self.data, changed)

    def test_available_ambiqsuite_tree_and_artifacts_authenticate(self) -> None:
        if not AVAILABLE_SDK.is_dir():
            self.skipTest("independent AmbiqSuite 5.1.0 package is unavailable")
        report = self.analyzer.audit(self.data, self.manifest, AVAILABLE_SDK)
        sdk = report["sdk_candidate_verification"]
        self.assertIsNotNone(sdk)
        assert sdk is not None
        self.assertEqual(sdk["file_count"], 50)
        self.assertEqual(sdk["byte_count"], 3_913_845)
        self.assertEqual(
            sdk["subtree_git_tree_sha1"],
            "e690768a6e7b4d6a8d526fc75e8278a2764deff3",
        )
        self.assertEqual(sdk["selected_artifacts_verified"], 10)
        self.assertEqual(sdk["gpu_patch_functions_verified"], 11)
        self.assertEqual(sdk["sdk_revision"], "release_sdk5p1p0-634f7c117b")

    def test_sdk_tree_mutation_is_rejected_when_candidate_is_available(self) -> None:
        if not AVAILABLE_SDK.is_dir():
            self.skipTest("independent AmbiqSuite 5.1.0 package is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-nemagfx-sdk-") as temp:
            candidate = Path(temp) / "AmbiqSuite_v5"
            shutil.copytree(AVAILABLE_SDK, candidate)
            cmake = candidate / "components/graphics/NemaGFX_SDK/CMakeLists.txt"
            cmake.write_bytes(cmake.read_bytes() + b"\n")
            with self.assertRaises(self.analyzer.AuditError):
                self.analyzer.audit(self.data, self.manifest, candidate)

    def test_cli_default_and_sdk_json_modes(self) -> None:
        default = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(default.stdout)
        self.assertEqual(report["dependency_identity"]["nemagfx_version"]["semantic_version"], "1.4.12")
        self.assertIsNone(report["sdk_candidate_verification"])
        if AVAILABLE_SDK.is_dir():
            verified = subprocess.run(
                [
                    sys.executable,
                    str(ANALYZER),
                    "--sdk-root",
                    str(AVAILABLE_SDK),
                    "--json",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(verified.stdout)["sdk_candidate_verification"][
                    "subtree_git_tree_sha1"
                ],
                "e690768a6e7b4d6a8d526fc75e8278a2764deff3",
            )


if __name__ == "__main__":
    unittest.main()
