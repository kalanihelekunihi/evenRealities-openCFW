#!/usr/bin/env python3
"""Guard the complete G2 Cordio common advertising evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_adv.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_adv", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmAdvAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_functions_abi_lineage_and_readiness_are_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["linked_function_count"], 9)
        self.assertEqual(module["linked_function_bytes"], 562)
        self.assertEqual(module["tu_bytes"], 572)
        self.assertEqual(module["literal_pool_bytes"], 10)
        self.assertEqual(module["direct_bl_ingress_sites"], 11)
        self.assertEqual(module["registered_function_entries"], 0)
        self.assertEqual(module["unexpected_aligned_entry_or_interior_pointers"], 0)
        self.assertEqual(len(module["source_only_dead_stripped"]), 6)
        self.assertEqual(self.report["abi"]["dm_num_adv_sets"], 2)
        self.assertEqual(self.report["abi"]["set_data_payload_offset"], 8)
        self.assertIn("flexible-array", self.report["abi"]["set_data_layout"])
        self.assertEqual(self.report["readiness"]["provider_seams"], 11)
        self.assertEqual(self.report["readiness"]["linked_unresolved_symbols"], 0)
        production = self.report["production"]
        self.assertEqual(production["status"], "routed")
        self.assertEqual(production["linked_functions"], 9)
        self.assertEqual(production["source_functions"], 15)
        self.assertEqual(production["stock_bytes_replaced"], 562)
        self.assertEqual(production["compiled_text_bytes"], 1122)
        self.assertEqual(production["alignment_bytes"], 20)
        self.assertEqual(production["strict_relocations"], 15)
        self.assertEqual(production["guarded_redirects"], 9)
        self.assertEqual(len(production["source_only_functions"]), 6)
        self.assertIn("blocked by unavailable physical evidence", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
