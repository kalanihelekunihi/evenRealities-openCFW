from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CordioDmSecAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "tools" / "analyze_g2_cordio_dm_sec.py"
        spec = importlib.util.spec_from_file_location("dm_sec_audit", path)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_stock_dm_sec_closure(self) -> None:
        report = self.module.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 8)
        self.assertEqual(module["linked_function_bytes"], 462)
        self.assertEqual(module["physical_bytes"], 488)
        self.assertEqual(module["source_inventory_functions"], 12)
        self.assertEqual(len(module["source_only_functions"]), 4)
        self.assertEqual(module["direct_bl_ingress_sites"], 23)
        self.assertEqual(module["registered_function_pointers"], 3)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertTrue(report["architecture"]["lesc_nonzero_ediv_rand_negative_reply"])
        self.assertEqual(report["architecture"]["security_component_id"], 5)
        self.assertEqual(report["architecture"]["lesc_component_id"], 8)
        self.assertEqual(report["abi"]["dm_sec_cb"], 0x20074114)
        self.assertEqual(report["abi"]["calc128_zeros"], 0x007856B0)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertEqual(report["production"]["stock_bytes_replaced"], 0)


if __name__ == "__main__":
    unittest.main()
