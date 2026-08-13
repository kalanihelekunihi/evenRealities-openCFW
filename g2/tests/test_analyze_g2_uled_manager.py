import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_uled_manager.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_uled_manager", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2UledManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 14,
            "body_bytes": 2332,
            "owned_noncode_bytes": 152,
            "physical_bytes": 2484,
            "direct_bl_entry_sites": 18,
            "exterior_bl_entry_sites": 17,
            "direct_body_calls": 97,
            "stored_entry_pointers": 1,
            "runtime_entry_materializations": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_instruction_windows": 15,
            "qualified_raw_overlap_windows": 1,
        })

    def test_panel_selection_and_dispatch(self) -> None:
        dispatch = self.report["dispatch"]
        self.assertEqual(dispatch["operations_records"], 2)
        self.assertEqual(dispatch["record_bytes"], 64)
        self.assertEqual(dispatch["callback_slots"], 15)
        self.assertEqual(dispatch["type_offset"], "0x3c")
        self.assertEqual(dispatch["configuration_key"], 1)
        self.assertEqual(dispatch["a6ng_selector_byte"], "0x06")
        self.assertEqual(dispatch["a6ng_type"], 1)
        self.assertEqual(dispatch["jbd4010_type"], 0)
        self.assertEqual(dispatch["clear_callback"], "0x004ca2ad")

    def test_framebuffer_contract(self) -> None:
        display = self.report["display"]
        self.assertEqual(display["framebuffer_pointer"], "0x200007b8")
        self.assertEqual((display["width"], display["height"]), (640, 480))
        self.assertEqual(display["bits_per_pixel"], 4)
        self.assertEqual(display["scanline_bytes"], 320)
        self.assertEqual((display["clamped_x_end"], display["clamped_y_end"]),
                         (639, 479))
        self.assertTrue(display["boundary_nibbles_preserved"])

    def test_remains_analysis_only(self) -> None:
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
