#!/usr/bin/env python3
"""Guard the partial stock inclusion of Cordio atts_sign.c."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_sign.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_sign", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsSignAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_configuration_api_survives_but_processing_path_is_stripped(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        exclusion = report["processing_exclusion"]
        self.assertEqual(module["classification"], "partially_linked_configuration_only")
        self.assertEqual(module["linked_function_count"], 4)
        self.assertEqual(module["linked_function_bytes"], 370)
        self.assertEqual(module["source_inventory_functions"], 8)
        self.assertEqual(len(module["source_only_functions"]), 4)
        self.assertTrue(exclusion["atts_init_installs_empty_sign_handler"])
        self.assertFalse(exclusion["atts_sign_init_linked"])
        self.assertFalse(exclusion["signed_write_processor_linked"])
        self.assertEqual(exclusion["later_sign_handler_installations"], 0)
        self.assertEqual(exclusion["signed_write_cmac_calls"], 0)
        self.assertEqual(report["abi"]["connection_record_stride"], 16)
        self.assertEqual(report["abi"]["authenticated_offset"], 12)
        self.assertTrue(report["lineage"]["authenticated_csrk_extension"])
        self.assertFalse(report["lineage"]["public_r20_api_exact"])
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
