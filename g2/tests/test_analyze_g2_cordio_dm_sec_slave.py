import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DmSecSlaveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "dm_sec_slave_audit", ROOT / "tools/analyze_g2_cordio_dm_sec_slave.py"
        )
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_closure(self):
        report = self.module.analyze()
        module = report["module"]
        self.assertEqual(
            (module["linked_function_count"], module["linked_function_bytes"], module["physical_bytes"]),
            (3, 148, 152),
        )
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(
            (module["direct_bl_ingress_sites"], module["registered_function_pointers"], module["strict_interior_pointers"]),
            (6, 0, 0),
        )
        self.assertEqual(report["architecture"]["ltk_response_event"], 0x29)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertTrue(report["production"]["production_routed"])
        self.assertEqual(report["production"]["live_functions"], 3)
        self.assertEqual(report["production"]["compiled_leaf_bytes"], 160)
        self.assertEqual(report["production"]["source_owned_bytes_added"], 164)
        self.assertEqual(report["production"]["stock_bytes_replaced"], 148)
        self.assertIn("blocked by unavailable physical evidence", report["production"]["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
