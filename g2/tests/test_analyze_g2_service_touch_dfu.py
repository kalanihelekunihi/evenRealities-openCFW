import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_service_touch_dfu.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_service_touch_dfu", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ServiceTouchDfuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 12,
            "restored_pathless_functions": 20,
            "linked_functions": 32,
            "body_bytes": 6430,
            "owned_gap_pool_bytes": 574,
            "physical_bytes": 7004,
            "direct_bl_entry_sites": 60,
            "external_direct_bl_entry_sites": 5,
            "direct_body_calls": 394,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 23,
        })

    def test_frame_package_and_program_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["package_path"], "/firmware/touch.bin")
        self.assertEqual(contract["package_magic"], "FWPK")
        self.assertEqual(contract["touch_firmware_type"], 3)
        self.assertEqual(contract["frame_start"], 1)
        self.assertEqual(contract["frame_terminator"], 0x17)
        self.assertEqual(contract["frame_payload_max_bytes"], 32)
        self.assertEqual(contract["reply_max_bytes"], 15)
        self.assertEqual(contract["send_retry_limit"], 100)
        self.assertEqual(contract["packet_bytes"], 32)
        self.assertEqual(contract["program_block_bytes"], 128)
        self.assertEqual(contract["commands"][0x49], "program_block")

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("service_touch_dfu.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 3)
        self.assertEqual(len(lineage["exact_symbols"]), 12)
        self.assertIn("TouchUpdateFirmwareCheck", lineage["exact_symbols"])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
