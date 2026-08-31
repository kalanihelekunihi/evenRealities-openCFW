# SPDX-License-Identifier: MIT
"""Admission tests for the deterministic EM9305 record-package wrapper."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/analyze_em9305_record_package.py"
SPEC = importlib.util.spec_from_file_location(
    "analyze_em9305_record_package", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import EM9305 record-package analyzer")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Em9305RecordPackageAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_authenticated_package_roundtrip_is_exact(self) -> None:
        self.assertEqual(
            self.report["status"],
            "record-package-software-closed-source-image-incomplete",
        )
        self.assertEqual(self.report["authenticated_stock"], {
            "path": "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin",
            "size": 211_948,
            "sha256":
                "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
        })
        self.assertTrue(self.report["stock_roundtrip_byte_exact"])
        self.assertTrue(self.report["software_wrapper_complete"])
        self.assertTrue(self.report["software_package_complete"])

    def test_record_and_erase_layout_is_exact(self) -> None:
        container = self.report["container"]
        self.assertEqual(container["magic_hex"], "00020404")
        self.assertEqual(container["metadata_bytes"], 124)
        self.assertEqual(container["payload_bytes"], 211_824)
        self.assertEqual(container["record_count"], 4)
        self.assertEqual(container["erase_sector_count"], 29)
        self.assertEqual(
            [(item["target_address"], item["size"])
             for item in container["records"]],
            list(MODULE.EXPECTED_RECORDS),
        )
        self.assertEqual(
            container["erase_sector_table_sha256"],
            "2c6e30cad70fd9817ce14dd1de8beb8cf6405a9b67db3adc0c9426c18d2935f0",
        )

    def test_source_and_hardware_gates_remain_fail_closed(self) -> None:
        self.assertFalse(self.report["source_records_complete"])
        self.assertFalse(self.report["source_image_complete"])
        self.assertFalse(self.report["production_routed"])
        self.assertEqual(len(self.report["remaining_software_blockers"]), 3)
        self.assertEqual(self.report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.report["hardware_operations"], [])

    def test_checked_manifest_matches_live_analysis(self) -> None:
        self.assertEqual(json.loads(MODULE.MANIFEST.read_text()), self.report)


if __name__ == "__main__":
    unittest.main()
