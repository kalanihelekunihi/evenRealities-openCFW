import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_at_tp.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_at_tp", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2AtTpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 2,
            "body_bytes": 898,
            "owned_noncode_bytes": 142,
            "physical_bytes": 1040,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 70,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        })

    def test_command_contract(self) -> None:
        command = self.report["command"]
        self.assertEqual(command["name"], "AT^TP")
        self.assertEqual(command["handler"], "_atTpTest")
        self.assertEqual(command["subcommands"], [
            "1", "0", "debug1", "debug0", "bsln_read", "bsln_set",
            "gesture_cfg_read", "gesture_cfg_set",
        ])
        self.assertEqual(command["debug_flag"], "0x20075017")
        self.assertEqual(command["gesture_threshold_ms"], [1, 65535])
        self.assertEqual(command["gesture_readback_delay_ms"], 100)

    def test_lineage_and_production_boundary(self) -> None:
        self.assertEqual(self.report["lineage"]["exact_symbol"], "_atTpTest")
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/at_tp.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["ownership_bytes"], 2590)
        self.assertEqual(production["source_functions"], 2)
        self.assertEqual(production["compiled_text_bytes"], 1548)
        self.assertEqual(production["alignment_bytes"], 2)
        self.assertEqual(production["stock_replaced_bytes"], 1040)
        self.assertEqual(production["strict_relocations"], 18)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")
        self.assertIn("required for future qualification", production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
