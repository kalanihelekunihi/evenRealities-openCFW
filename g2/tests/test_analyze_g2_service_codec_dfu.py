import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_service_codec_dfu.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_service_codec_dfu", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ServiceCodecDfuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 9,
            "restored_pathless_functions": 7,
            "linked_functions": 16,
            "body_bytes": 9052,
            "owned_gap_pool_bytes": 916,
            "physical_bytes": 9968,
            "direct_bl_entry_sites": 34,
            "external_direct_bl_entry_sites": 4,
            "direct_body_calls": 584,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 1,
        })

    def test_package_and_transfer_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["package_path"], "/firmware/codec.bin")
        self.assertEqual(contract["package_magic"], "FWPK")
        self.assertEqual(contract["package_header_bytes"], 16)
        self.assertEqual(contract["firmware_record_bytes"], 16)
        self.assertEqual(contract["firmware_types"], {1: "boot", 2: "firmware"})
        self.assertEqual(contract["stage1_uart_baud"], 230400)
        self.assertEqual(contract["boot_header_bytes"], 32)
        self.assertEqual(contract["transfer_chunk_bytes"], 256)
        self.assertEqual(contract["flash_scratch_bytes"], 8192)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("service_codec_dfu.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(lineage["exact_symbols"], [
            "SVC_CodecDfu", "SVC_CodecCheckAndUpgrade",
        ])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
