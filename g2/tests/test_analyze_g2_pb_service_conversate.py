import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_conversate.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_conversate", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceConversateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 6,
            "body_bytes": 1776,
            "owned_pool_bytes": 128,
            "physical_bytes": 1904,
            "direct_bl_entry_sites": 10,
            "direct_body_calls": 96,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 0,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "decode_failure": 5, "null": 6, "duplicate": 13,
        })
        self.assertEqual(contract["duplicate_window_ms"], 3000)
        self.assertEqual(contract["rx_hexdump_limit"], 0x20)
        self.assertEqual(contract["tx_status"], {
            "success": 0, "encode_failure": 5, "null": 6,
        })
        self.assertEqual([contract["route"], contract["service"]], [1, "0x0b"])
        self.assertEqual(contract["message_bytes"], 0xFAC)
        self.assertEqual(contract["encode_capacity"], 0x100)
        envelopes = contract["envelopes"]
        self.assertEqual(
            [(value["command"], value["tag"], value["send"]) for value in envelopes.values()],
            [(0xA1, 9, "notify"), (2, 4, "notify"), (4, 6, "notify"),
             (0xA2, 10, "tx"), (0xA3, 12, "notify")],
        )
        self.assertEqual(envelopes["tag_tracking"]["payload_bytes"], 12)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_conversate.c"))
        self.assertEqual(lineage["path_pointer_cells"], ["0x005b2244"])
        self.assertEqual(len(lineage["exact_symbols"]), 6)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_conversate.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 1776)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 8)
        self.assertEqual(production["compiled_text_bytes"], 1098)
        self.assertEqual(production["alignment_bytes"], 8)
        self.assertEqual(production["strict_relocations"], 33)
        self.assertEqual(production["stock_replaced_bytes"], 1776)
        self.assertEqual(production["retained_literal_pool_bytes"], 128)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")


if __name__ == "__main__":
    unittest.main()
