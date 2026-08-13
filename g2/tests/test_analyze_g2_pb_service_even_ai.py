import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_even_ai.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_even_ai", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceEvenAiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 25,
            "body_bytes": 8404,
            "owned_gap_pool_bytes": 552,
            "physical_bytes": 8956,
            "assertion_records": 23,
            "direct_bl_entry_sites": 26,
            "direct_body_calls": 494,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 89,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "handler_or_duplicate": 1,
            "null": 2, "decode_failure": 0x2B,
        })
        self.assertEqual(contract["duplicate_state"], "0x20074f36")
        self.assertIn("no time window", contract["duplicate_policy"])
        self.assertEqual(contract["tx_status"]["encode_failure"], 0x2B)
        self.assertEqual([contract["route"], contract["service"]], [1, 7])
        self.assertEqual(contract["message_bytes"], 0x20C)
        self.assertEqual(contract["encode_capacity"], 0x100)
        self.assertEqual(
            [(item["command"], item["tag"]) for item in contract["command_tags"]],
            [(value, value + 2) for value in range(1, 11)],
        )
        self.assertEqual(contract["notifications"], ["control", "vad", "event"])
        self.assertEqual(contract["command_response"], {
            "command": 0xA1, "tag": 12, "payload_bytes": 1, "send": "tx",
        })

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_even_ai.c"))
        self.assertEqual(lineage["path_pointer_cells"], 28)
        self.assertEqual(len(lineage["exact_symbols"]), 25)
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
