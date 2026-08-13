import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_ota_service.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_ota_service", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2OtaServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 12,
            "restored_pathless_functions": 13,
            "linked_functions": 25,
            "body_bytes": 15394,
            "owned_gap_pool_bytes": 982,
            "physical_bytes": 16376,
            "direct_bl_entry_sites": 107,
            "external_direct_bl_entry_sites": 39,
            "direct_body_calls": 855,
            "intra_body_b_w_targets": 14,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 81,
        })

    def test_protocol_and_storage_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["frame_ids"], {
            0xC0: "import_control", 0xC1: "raw_or_status",
            0xC2: "export_control", 0xC3: "export_control_alt",
        })
        self.assertEqual(contract["transfer_state_bytes"], 0x70)
        self.assertEqual(contract["export_state_bytes"], 0x60)
        self.assertEqual(contract["chunk_capacity"], 0x1000)
        self.assertEqual(contract["notification_payloads_le"], [0x0402, 0x0302, 0x0502])
        self.assertTrue(contract["read_after_write_verification"])

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("ota_service.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 7)
        self.assertEqual(len(lineage["exact_symbols"]), 12)
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
