import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DmConnSlaveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "dm_conn_slave_audit", ROOT / "tools/analyze_g2_cordio_dm_conn_slave.py"
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
            (5, 206, 212),
        )
        self.assertEqual(module["source_only_functions"], ["DmConnAccept"])
        self.assertEqual(
            (module["direct_bl_ingress_sites"], module["registered_function_pointers"], module["strict_interior_pointers"]),
            (5, 2, 0),
        )
        self.assertEqual(module["unaligned_false_pointer_windows"], 1)
        self.assertEqual(report["architecture"]["l2c_update_confirm_event"], 0x73)
        self.assertTrue(report["architecture"]["separate_update_component"])
        self.assertEqual(report["architecture"]["update_executor"], "dmConnUpdExecute")
        self.assertEqual(report["build_readiness"]["status"], "target-compiled")
        production=report["production"]
        self.assertEqual(production["status"],"production-routed")
        self.assertEqual((production["redirected_stock_functions"],production["redirected_stock_bytes"]),(5,206))
        self.assertEqual((production["source_owned_bytes_added"],production["alignment_bytes_added"],production["strict_relocations"]),(256,6,7))
        self.assertEqual(production["manifest_regions"],13)
        self.assertGreater(production["flash_plan_counts"][0],0)
        self.assertEqual(production["flash_plan_counts"][1],0)


if __name__ == "__main__":
    unittest.main()
