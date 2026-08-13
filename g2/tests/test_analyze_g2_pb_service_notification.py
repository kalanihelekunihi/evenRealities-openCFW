import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_notification.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_notification", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceNotificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 9, "body_bytes": 3318,
            "owned_gap_pool_bytes": 238, "physical_bytes": 3556,
            "assertion_records": 7, "direct_bl_entry_sites": 10,
            "direct_body_calls": 202, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 3,
        })

    def test_notification_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "null": 2, "decode_failure": 0x2B,
        })
        self.assertEqual(contract["whitelist_check_status"], {
            "cache_invalid": 1, "match": 2, "mismatch": 3,
        })
        self.assertEqual(list(contract["commands"]), [1, 2, 3, 4, 0xA1])
        self.assertEqual([contract["route"], contract["service"]], [1, 4])
        self.assertEqual([contract["message_bytes"], contract["encode_capacity"]],
                         [0x4C, 0x100])

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_notification.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 9)
        self.assertEqual(len(lineage["exact_symbols"]), 9)
        self.assertEqual(lineage["assertion_lines"],
                         [103, 122, 160, 243, 259, 296, 312])
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
