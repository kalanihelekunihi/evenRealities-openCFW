import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_imu_icm45608.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_imu_icm45608", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2Icm45608Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 11,
            "restored_non_anchor_functions": 42,
            "linked_functions": 53,
            "body_bytes": 11674,
            "owned_gap_pool_bytes": 762,
            "physical_bytes": 12436,
            "direct_bl_entry_sites": 72,
            "external_direct_bl_entry_sites": 35,
            "direct_body_calls": 464,
            "stored_exact_entry_pointers": 3,
            "strict_interior_bl_ingress": 0,
            "internal_b_w_epilogue_branches": 10,
            "external_b_w_ingress": 0,
            "raw_entry_or_interior_windows": 21,
        })

    def test_sample_ring_and_raw_capture_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["sample_ring_address"], "0x200640a0")
        self.assertEqual(contract["sample_ring_header_bytes"], 12)
        self.assertEqual(contract["sample_slots"], 20)
        self.assertEqual(contract["sample_stride"], 0x70)
        self.assertEqual(contract["raw_collection_limit_ms"], 120000)
        self.assertEqual(contract["accel_config_min_interval"], 100)
        self.assertEqual(contract["accel_config_max_interval"], 4999)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("imu_icm45608.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 15)
        self.assertIn("DRV_IMUDataParserCallback", lineage["exact_symbols"])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertEqual(lineage["tdk_exact_abi_tag"], "1.1.2")
        self.assertEqual(
            lineage["tdk_exact_abi_commit"],
            "b79ae575f7f310e5ae2e1164096d1a858bb74662",
        )
        self.assertEqual(lineage["tdk_snapshot_license"], "BSD-3-Clause")
        self.assertEqual(lineage["tdk_snapshot_files"], 52)
        self.assertEqual(lineage["tdk_snapshot_bytes"], 594177)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/imu_icm45608.c",
        )
        self.assertTrue(production["source_inventory_available"])
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["source_functions"], 54)
        self.assertEqual(production["tdk_primary_functions"], 143)
        self.assertEqual(production["total_source_functions"], 197)
        self.assertEqual(production["recovered_functions"], 53)
        self.assertEqual(production["compiled_text_bytes"], 8610)
        self.assertEqual(production["tdk_compiled_function_bytes"], 54128)
        self.assertEqual(production["tdk_build_source_files"], 8)
        self.assertEqual(production["tdk_build_source_bytes"], 184197)
        self.assertEqual(production["generated_alignment_bytes"], 30)
        self.assertEqual(production["guarded_redirects"], 52)
        self.assertEqual(production["authenticated_relocations"], 83)
        self.assertEqual(production["manifest_regions"], 143)
        self.assertEqual(production["ownership_bytes"], 11672)
        self.assertTrue(production["source_owned_device_initialization"])
        self.assertTrue(production["exact_three_argument_transport_abi"])
        self.assertTrue(production["source_owned_fifo_acquisition"])
        self.assertTrue(production["source_owned_register_polling"])
        self.assertTrue(production["source_owned_edmp_gaf_configuration"])
        self.assertTrue(production["source_owned_gaf_decode"])
        self.assertTrue(production["source_owned_magnetometer_i2cm"])
        self.assertTrue(production["source_owned_extended_edmp_images"])
        self.assertTrue(production["source_owned_aid_b2s_configuration"])
        self.assertTrue(production["source_owned_aid_b2s_event_routing"])
        self.assertIsNone(production["remaining_software_gap"])
        self.assertEqual(
            production["hardware_validation"],
            "blocked_unavailable_physical_evidence",
        )


if __name__ == "__main__":
    unittest.main()
