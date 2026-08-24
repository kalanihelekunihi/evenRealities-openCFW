import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_pair_mgr.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_pair_mgr", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServicePairMgrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 20, "path_correlated_anchors": 17,
            "restored_helpers": 3, "body_bytes": 6564,
            "owned_gap_pool_bytes": 724, "physical_bytes": 7288,
            "assertion_records": 23, "direct_bl_entry_sites": 25,
            "direct_body_calls": 418, "stored_exact_entry_pointers": 6,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(list(contract["commands"]), [4, 5, 6, 7, 8, 9])
        self.assertEqual([contract["route"], contract["service"]], [1, 0x80])
        self.assertEqual(contract["notification_allocation_bytes"], 0x1A8)
        self.assertEqual(contract["ring_mac_bytes"], 6)
        self.assertEqual(contract["stored_notification_callback"], "0x004bc419")

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_pair_mgr.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 26)
        self.assertEqual(len(lineage["exact_symbols"]), 18)
        self.assertEqual(len(lineage["assertion_lines"]), 23)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_pair_mgr.c",
        )
        self.assertTrue(production["source_inventory_available"])
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 6564)
        self.assertEqual(production["source_functions"], 21)
        self.assertEqual(production["compiled_text_bytes"], 2300)
        self.assertEqual(production["alignment_bytes"], 22)
        self.assertEqual(production["strict_relocations"], 97)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")
        self.assertIn("No authorized responsive G2", production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
