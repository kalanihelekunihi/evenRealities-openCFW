#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_app_connect_params.py"


class AppConnectParamsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_app_connect_params", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_closed_object(self) -> None:
        report = self.module.analyze()
        surface = report["surface"]
        self.assertEqual(surface["linked_functions"], 14)
        self.assertEqual(surface["path_anchored_functions"], 10)
        self.assertEqual(surface["additional_recovered_functions"], 4)
        self.assertEqual(surface["body_bytes"], 6_336)
        self.assertEqual(surface["literal_pool_bytes"], 552)
        self.assertEqual(surface["physical_bytes"], 6_888)
        self.assertEqual(surface["stored_entry_pointers"], 3)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 2)

    def test_identity_and_behavior(self) -> None:
        report = self.module.analyze()
        self.assertEqual(
            report["identity"]["ownership"],
            "g2_local_cordio_connection_parameter_policy",
        )
        self.assertIsNone(report["identity"]["third_party_dependency"])
        self.assertEqual(report["behavior"]["fast_interval_threshold_units"], 25)
        self.assertEqual(report["behavior"]["slow_interval_threshold_units"], 72)
        self.assertEqual(report["behavior"]["connection_ids"], [1, 2, 3])
        self.assertEqual(report["cross_version"]["older_only_function"], "ble_conn_param_log_format")
        self.assertFalse(report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
