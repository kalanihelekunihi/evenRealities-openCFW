import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_terminal_pb_msg_handler.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_terminal_pb_msg_handler", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2TerminalPbMsgHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 10,
            "restored_pathless_functions": 17,
            "linked_functions": 27,
            "body_bytes": 7688,
            "owned_gap_pool_bytes": 676,
            "physical_bytes": 8364,
            "direct_bl_entry_sites": 56,
            "external_direct_bl_entry_sites": 12,
            "direct_body_calls": 432,
            "stored_exact_entry_pointers": 14,
            "raw_direct_interior_candidates": 1,
            "classified_instruction_overlaps": 1,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 54,
        })

    def test_dispatch_and_state_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["event_min"], 0)
        self.assertEqual(contract["event_max"], 12)
        self.assertIsNone(contract["event_actions"][0])
        self.assertEqual(contract["event_actions"][5], "agent_content")
        self.assertEqual(contract["event_actions"][12], "session_id_changed")
        self.assertEqual(contract["states_allowing_runtime_event"], [0, 2, 7, 11, 12])
        self.assertEqual(contract["processing_states"], [1, 2, 3])
        self.assertEqual(contract["session_list_log_limit"], 10)
        self.assertEqual(contract["tool_start_dedup_ms"], 2000)
        self.assertEqual(len(contract["callback_pointer_cells"]), 2)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("terminal_pb_msg_handler.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 19)
        self.assertIn("terminal_machine_handler", lineage["exact_symbols"])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
