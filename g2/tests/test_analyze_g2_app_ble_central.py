#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_app_ble_central.py"


class AppBleCentralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_app_ble_central", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_closed_object(self) -> None:
        report = self.module.analyze()
        surface = report["surface"]
        self.assertEqual(surface["linked_functions"], 44)
        self.assertEqual(surface["path_anchored_functions"], 24)
        self.assertEqual(surface["additional_recovered_functions"], 20)
        self.assertEqual(surface["recursive_decode_recoveries"], 6)
        self.assertEqual(surface["body_bytes"], 14_288)
        self.assertEqual(surface["literal_pool_bytes"], 1_464)
        self.assertEqual(surface["physical_bytes"], 15_752)
        self.assertEqual(surface["stored_entry_pointers"], 17)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 1)

    def test_identity_and_behavior(self) -> None:
        report = self.module.analyze()
        self.assertEqual(
            report["identity"]["ownership"],
            "g2_local_cordio_central_role_and_ringlink_policy",
        )
        self.assertIsNone(report["identity"]["third_party_dependency"])
        self.assertEqual(report["behavior"]["application_event_ids"], list(range(0xAE, 0xB5)))
        self.assertEqual(len(report["behavior"]["ringlink_states"]), 7)
        self.assertFalse(report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
