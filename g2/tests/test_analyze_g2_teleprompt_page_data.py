import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_teleprompt_page_data.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_teleprompt_page_data", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2TelepromptPageDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 9,
            "restored_non_anchor_functions": 12,
            "linked_functions": 21,
            "body_bytes": 4728,
            "owned_gap_pool_bytes": 392,
            "physical_bytes": 5120,
            "direct_bl_entry_sites": 81,
            "external_direct_bl_entry_sites": 17,
            "direct_body_calls": 276,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 2,
        })

    def test_ring_cache_and_window_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["state_bytes"], 0x51A4)
        self.assertEqual(contract["slot_count"], 20)
        self.assertEqual(contract["slot_stride"], 0x414)
        self.assertEqual(contract["page_copy_bytes"], 0x40C)
        self.assertEqual(contract["slot_status_offset"], 0x40C)
        self.assertEqual(contract["slot_request_time_offset"], 0x410)
        self.assertEqual(contract["visible_window_pages"], 4)
        self.assertEqual(contract["ensure_pages_before"], 5)
        self.assertEqual(contract["ensure_pages_after"], 8)
        self.assertEqual(contract["request_debounce_ms"], 500)
        self.assertEqual(contract["loading_timeout_ms"], 5000)
        self.assertEqual(contract["preload_timer_ms"], 2500)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("teleprompt_page_data.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 2)
        self.assertEqual(len(lineage["exact_symbols"]), 10)
        self.assertIn("teleprompt_preload_timer_callback", lineage["exact_symbols"])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
