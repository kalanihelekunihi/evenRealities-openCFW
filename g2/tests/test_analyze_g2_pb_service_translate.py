import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_translate.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_translate", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceTranslateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 4,
            "body_bytes": 1324,
            "owned_pool_bytes": 120,
            "physical_bytes": 1444,
            "direct_bl_entry_sites": 8,
            "direct_body_calls": 74,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 28,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "decode_failure": 5, "null": 6, "duplicate": 13,
        })
        self.assertEqual(contract["duplicate_window_ms"], 3000)
        self.assertEqual(contract["tx_status"], {"success": 0, "encode_failure": 5, "null": 6})
        self.assertEqual(
            [contract["notify_subtype"], contract["mode_switch_subtype"], contract["command_response_subtype"]],
            [5, 6, 7],
        )
        self.assertEqual(contract["shared_message_bytes"], 0x854)
        self.assertEqual(contract["encode_capacity"], 0x100)

    def test_lineage_and_production_boundary(self) -> None:
        self.assertTrue(self.report["lineage"]["retained_path"].endswith("pb_service_translate.c"))
        self.assertEqual(len(self.report["lineage"]["exact_symbols"]), 4)
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
