#!/usr/bin/env python3
"""Guard the fail-closed stock exclusion of Cordio attc_sign.c."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_sign.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_sign", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttcSignAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_optional_client_signing_is_absent(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        exclusion = report["exclusion"]
        self.assertEqual(module["classification"], "not_linked_or_dead_stripped")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["source_inventory_functions"], 7)
        self.assertEqual(len(module["source_only_functions"]), 7)
        self.assertEqual(exclusion["attc_control_block"], 0x2006F904)
        self.assertEqual(exclusion["sign_interface_offset"], 0x1B0)
        self.assertTrue(exclusion["attc_init_clears_sign_interface"])
        self.assertEqual(exclusion["later_sign_interface_installations"], 0)
        self.assertEqual(exclusion["sign_interface_direct_literals"], 0)
        self.assertEqual(exclusion["signed_write_wrapper_candidates"], 0)
        self.assertEqual(exclusion["retained_name_or_path_markers"], 0)
        self.assertFalse(report["lineage"]["stock_body_version_discriminated"])
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
