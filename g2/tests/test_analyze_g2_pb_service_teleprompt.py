import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_teleprompt.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_teleprompt", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceTelepromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 7,
            "body_bytes": 1854,
            "owned_tail_bytes": 130,
            "physical_bytes": 1984,
            "direct_bl_entry_sites": 11,
            "direct_body_calls": 98,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "false_halfword_bl_candidates": 1,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "decode_failure": 5, "null": 6, "duplicate": 13,
        })
        self.assertEqual(contract["duplicate_window_ms"], 3000)
        self.assertEqual(contract["rx_hexdump_limit"], 0x20)
        self.assertEqual(contract["tx_status"], {
            "success": 0, "encode_failure": 0x2B,
        })
        self.assertFalse(contract["tx_pointer_null_guards"])
        self.assertEqual([contract["route"], contract["service"]], [1, 6])
        self.assertEqual(contract["message_bytes"], 0xF58)
        self.assertEqual(contract["encode_capacity"], 0x100)
        envelopes = contract["envelopes"]
        self.assertEqual(
            [(value["command"], value["tag"], value["send"])
             for value in envelopes.values()],
            [(0xA6, 12, "tx"), (0xA1, 7, "notify"),
             (0xA2, 8, "notify"), (0xA3, 9, "notify"),
             (0xA4, 10, "notify"), (0xA5, 11, "notify")],
        )
        self.assertEqual(
            [value["payload_bytes"] for value in envelopes.values()],
            [1, 2, 1, 0x42, 4, 12],
        )
        self.assertTrue(envelopes["command_response"]["caller_magic"])

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_teleprompt.c"))
        self.assertEqual(lineage["path_pointer_cells"], ["0x00588cfc"])
        self.assertEqual(len(lineage["exact_symbols"]), 7)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_teleprompt.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 1854)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 9)
        self.assertEqual(production["compiled_text_bytes"], 1348)
        self.assertEqual(production["alignment_bytes"], 4)
        self.assertEqual(production["strict_relocations"], 39)
        self.assertEqual(production["stock_replaced_bytes"], 1854)
        self.assertEqual(production["retained_literal_pool_bytes"], 130)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
