import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_quicklist.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_quicklist", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceQuicklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 10, "body_bytes": 3468,
            "owned_gap_pool_bytes": 280, "physical_bytes": 3748,
            "assertion_records": 8, "direct_bl_entry_sites": 10,
            "direct_body_calls": 199, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "null": 2, "decode_failure": 0x2B,
            "success": "handler_or_transmit_result",
        })
        self.assertEqual(contract["tx_status"], {
            "success": 0, "null": 2, "encode_failure": 0x2B,
            "notify_failure": -1,
        })
        self.assertEqual(contract["commands"], {
            1: "item_tag_3", 2: "multi_items_tag_4", 3: "event_tag_5",
        })
        self.assertEqual([contract["route"], contract["service"]], [1, 0x0C])
        self.assertEqual(contract["decoded_message_bytes"], 0x1238)
        self.assertEqual(contract["transmit_message_bytes"], 0x1238)
        self.assertEqual(contract["encode_capacity"], 0x400)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_quicklist.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 11)
        self.assertEqual(len(lineage["exact_symbols"]), 10)
        self.assertEqual(lineage["assertion_lines"], [151, 165, 240, 254,
                                                       290, 331, 344, 380])
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
