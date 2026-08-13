import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_uled_jbd4010.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_uled_jbd4010", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2UledJbd4010Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 24,
            "body_bytes": 4588,
            "owned_noncode_bytes": 348,
            "physical_bytes": 4936,
            "direct_bl_entry_sites": 77,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 289,
            "stored_entry_pointers": 14,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 7,
        })

    def test_panel_request_and_dispatch_abi(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["request_bytes"], 28)
        self.assertEqual(abi["request_templates"], 4)
        self.assertEqual(abi["mspi_handle"], "0x20074524")
        self.assertEqual(abi["framebuffer"], "0x20074528")
        self.assertEqual(abi["clear_callback"], "0x2007452c")
        self.assertEqual(abi["operations_callbacks"], 14)

    def test_display_protocol(self) -> None:
        display = self.report["display"]
        self.assertEqual((display["width"], display["height"]), (640, 480))
        self.assertEqual(display["bits_per_pixel"], 4)
        self.assertEqual(display["scanline_bytes"], 320)
        self.assertEqual(display["offset_x_range"], [2, 22])
        self.assertEqual(display["offset_y_range"], [2, 18])
        self.assertEqual(display["accepted_modes"], [0x71, 0x72, 0x73, 0x74])
        self.assertEqual(display["die_id_bytes"], 12)

    def test_remains_analysis_only(self) -> None:
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
