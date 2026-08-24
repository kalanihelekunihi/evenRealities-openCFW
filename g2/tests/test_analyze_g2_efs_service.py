import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_efs_service.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_efs_service", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2EfsServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 6,
            "restored_pathless_functions": 6,
            "linked_functions": 12,
            "body_bytes": 9276,
            "owned_gap_pool_bytes": 658,
            "physical_bytes": 9934,
            "direct_bl_entry_sites": 35,
            "external_direct_bl_entry_sites": 10,
            "direct_body_calls": 559,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 8,
        })

    def test_protocol_and_storage_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["frame_ids"], {
            0xC4: "import_control", 0xC5: "import_raw_data",
            0xC6: "export_control", 0xC7: "export_data",
        })
        self.assertEqual(contract["file_types"], {
            0: "notification_whitelist", 1: "android_message_json",
            2: "logger_export", 3: "tracepoint_export", 0xAA: "other_file",
        })
        self.assertEqual(contract["transfer_state_bytes"], 0x78)
        self.assertEqual(contract["chunk_capacity"], 0x1000)
        self.assertEqual(contract["android_message_capacity"], 0x2137)

    def test_lineage_and_production_closure(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("efs_service.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 6)
        self.assertEqual(lineage["observed_source_lines"], [
            262, 287, 334, 347, 519, 543, 620, 648, 834, 936, 947,
        ])
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/efs_service.c",
        )
        self.assertTrue(production["source_inventory_available"])
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 9276)
        self.assertEqual(production["source_functions"], 12)
        self.assertEqual(production["compiled_text_bytes"], 2936)
        self.assertEqual(production["alignment_bytes"], 16)
        self.assertEqual(production["strict_relocations"], 68)
        self.assertEqual(production["retained_gap_pool_bytes"], 658)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")
        self.assertIn("No authorized responsive G2 peer", production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
