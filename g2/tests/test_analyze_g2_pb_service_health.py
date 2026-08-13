import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_health.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_health", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface_and_missed_body(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 8, "body_bytes": 3092,
            "owned_gap_pool_bytes": 312, "physical_bytes": 3404,
            "assertion_records": 8, "direct_bl_entry_sites": 8,
            "direct_body_calls": 180, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
            "manually_restored_bodies": 1,
        })

    def test_health_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "helper_failure": 1, "null": 2,
        })
        self.assertEqual(contract["tx_status"], {
            "success": 0, "encode_failure": 0x2B, "null": 2,
        })
        self.assertEqual(list(contract["envelopes"]), [1, 2, 3, 4])
        self.assertEqual([contract["route"], contract["service"]], [1, 0x0E])
        self.assertEqual([contract["message_bytes"], contract["encode_capacity"]],
                         [0x31C, 0x100])
        self.assertEqual(contract["multi_highlight_count_bits"], 16)
        self.assertFalse(contract["multi_highlight_wrapper_has_explicit_count_bound"])

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_health.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 10)
        self.assertEqual(len(lineage["exact_symbols"]), 8)
        self.assertEqual(lineage["assertion_lines"],
                         [109, 132, 213, 237, 313, 336, 374, 398])
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
