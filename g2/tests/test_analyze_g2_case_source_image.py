# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/analyze_g2_case_source_image.py"
SPEC = importlib.util.spec_from_file_location("analyze_case_source_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CaseSourceImageAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_source_graph_is_linked_and_packaged(self) -> None:
        metrics = self.report["metrics"]
        self.assertTrue(self.report["software_link_complete"])
        self.assertTrue(self.report["software_package_complete"])
        self.assertEqual(metrics["source_translation_units"], 8)
        self.assertEqual(metrics["linked_open_cfw_globals"], 223)
        self.assertEqual(metrics["undefined_symbols"], 0)
        self.assertEqual(metrics["covered_function_frontier"], 222)

    def test_hardware_contracts_remain_fail_closed(self) -> None:
        self.assertFalse(self.report["physical_board_services_routed"])
        self.assertFalse(self.report["production_routed"])
        self.assertEqual(self.report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.report["hardware_operations"], [])

    def test_written_manifest_matches(self) -> None:
        self.assertEqual(json.loads(MODULE.MANIFEST.read_text()), self.report)

    def test_complete_source_image_build_is_deterministic(self) -> None:
        builder = MODULE.load_builder()
        with tempfile.TemporaryDirectory(prefix="g2-case-image-a-") as first_dir, \
                tempfile.TemporaryDirectory(prefix="g2-case-image-b-") as second_dir:
            first = builder.build(Path(first_dir))
            second = builder.build(Path(second_dir))
        self.assertEqual(first["source_inventory"], second["source_inventory"])
        for artifact in ("elf", "raw", "even"):
            self.assertEqual(first[artifact]["size"], second[artifact]["size"])
            self.assertEqual(first[artifact]["sha256"], second[artifact]["sha256"])


if __name__ == "__main__":
    unittest.main()
