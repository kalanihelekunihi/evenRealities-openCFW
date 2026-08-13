#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_app_ble_peripheral.py"


class AppBlePeripheralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_app_ble_peripheral", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_closed_object(self) -> None:
        report = self.module.analyze()
        surface = report["surface"]
        self.assertEqual(surface["linked_functions"], 31)
        self.assertEqual(surface["path_anchored_functions"], 12)
        self.assertEqual(surface["additional_recovered_functions"], 19)
        self.assertEqual(surface["recursive_decode_recoveries"], 7)
        self.assertEqual(surface["body_bytes"], 5_888)
        self.assertEqual(surface["literal_pool_bytes"], 672)
        self.assertEqual(surface["physical_bytes"], 6_560)
        self.assertEqual(surface["stored_entry_pointers"], 8)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_dependency_boundary_and_behavior(self) -> None:
        report = self.module.analyze()
        self.assertEqual(
            report["identity"]["ownership"],
            "g2_local_cordio_peripheral_role_policy",
        )
        self.assertIsNone(report["identity"]["third_party_dependency"])
        self.assertEqual(
            report["third_party_boundary"]["selected_commit"],
            "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f",
        )
        self.assertEqual(report["behavior"]["normal_fast_window_ms"], 30_000)
        self.assertEqual(report["behavior"]["firmware_version_in_advertising"], "2.2.6.10")
        self.assertFalse(report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
