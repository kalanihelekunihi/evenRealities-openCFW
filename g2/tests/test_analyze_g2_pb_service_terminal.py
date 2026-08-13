import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_terminal.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_terminal", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceTerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 13,
            "body_bytes": 2554,
            "owned_tail_bytes": 246,
            "physical_bytes": 2800,
            "direct_bl_entry_sites": 33,
            "direct_body_calls": 130,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 15,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "decode_failure": 5, "null": 6, "duplicate": 13,
        })
        self.assertEqual(contract["duplicate_window_ms"], 3000)
        self.assertEqual(contract["tx_status"], {
            "success": 0, "encode_failure": 5, "unsupported_tag": 8, "null": 6,
        })
        self.assertEqual([contract["route"], contract["service"]], [1, 0x30])
        self.assertEqual(contract["message_bytes"], 0x850)
        self.assertEqual(contract["encode_capacity"], 0x878)
        self.assertEqual(
            [(item["command"], item["tag"], item["payload_bytes"])
             for item in contract["command_tags"]],
            [(0xA1, 9, 2), (0xA2, 10, 1), (0xA3, 11, 8),
             (0xA4, 12, 1), (0xA5, 18, 8), (0xA6, 19, 4),
             (0xA7, 20, 12), (0xA8, 22, 1), (0xA9, 24, 4),
             (0xAA, 25, 8)],
        )
        self.assertEqual(contract["command_response"], {
            "command": 0xF0, "tag": 13, "payload_bytes": 1, "send": "tx",
        })

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_terminal.c"))
        self.assertEqual(lineage["path_pointer_cells"], ["0x005cf1d4"])
        self.assertEqual(len(lineage["exact_symbols"]), 13)
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
