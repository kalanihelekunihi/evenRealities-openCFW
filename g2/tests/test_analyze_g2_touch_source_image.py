# SPDX-License-Identifier: MIT
"""Fail-closed tests for the aggregate Touch source image admission."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/analyze_g2_touch_source_image.py"
SPEC = importlib.util.spec_from_file_location("analyze_touch_source_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TouchSourceImageAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_source_graph_is_linked_and_packaged(self) -> None:
        self.assertTrue(self.report["software_link_complete"])
        self.assertTrue(self.report["software_package_complete"])
        self.assertEqual(self.report["metrics"]["source_translation_units"], 31)
        self.assertEqual(self.report["metrics"]["linked_open_cfw_globals"], 176)
        self.assertEqual(self.report["metrics"]["undefined_symbols"], 0)
        self.assertLessEqual(self.report["metrics"]["raw_flash_bytes"], 65536)

    def test_artifact_identity_and_source_inventory_are_pinned(self) -> None:
        self.assertEqual(len(self.report["artifacts"]["source_inventory"]), 32)
        self.assertTrue(all(len(row["sha256"]) == 64
                            for row in self.report["artifacts"]["source_inventory"]))
        self.assertTrue(all(len(self.report["artifacts"][key]) == 64 for key in (
            "elf_sha256", "raw_sha256", "fwpk_sha256")))

    def test_physical_routing_remains_fail_closed(self) -> None:
        self.assertFalse(self.report["physical_board_services_routed"])
        self.assertFalse(self.report["production_routed"])
        self.assertEqual(self.report["hardware_validation"],
                         "deferred by project direction")
        self.assertEqual(self.report["hardware_operations"], [])
        self.assertEqual(self.report["hardware_blocker"],
                         "deferred by project direction")

    def test_written_manifest_matches_live_analysis(self) -> None:
        stored = json.loads(MODULE.MANIFEST.read_text())
        self.assertEqual(stored, self.report)


if __name__ == "__main__":
    unittest.main()
