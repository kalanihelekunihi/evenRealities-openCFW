import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DmConnSlaveLegTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "dm_conn_slave_leg_audit", ROOT / "tools/analyze_g2_cordio_dm_conn_slave_leg.py"
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
            (5, 104, 120),
        )
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(
            (module["direct_bl_ingress_sites"], module["registered_function_pointers"], module["strict_interior_pointers"]),
            (1, 4, 0),
        )
        self.assertEqual(report["architecture"]["main_action_entries"], 4)
        self.assertEqual(report["architecture"]["update_action_entries"], 2)
        self.assertTrue(report["architecture"]["separate_update_table"])
        self.assertTrue(report["architecture"]["task_locked_init"])
        self.assertEqual(report["build_readiness"]["status"], "deferred")


if __name__ == "__main__":
    unittest.main()
