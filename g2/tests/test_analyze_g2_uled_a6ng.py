import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_uled_a6ng.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_uled_a6ng", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2UledA6ngTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 22,
            "body_bytes": 5276,
            "owned_noncode_bytes": 444,
            "physical_bytes": 5720,
            "direct_bl_entry_sites": 99,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 366,
            "stored_entry_pointers": 15,
            "strict_interior_ingress": 0,
            "qualified_vfp_windows": 4,
            "qualified_raw_overlap_windows": 2,
        })

    def test_panel_request_and_dispatch_abi(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["request_bytes"], 28)
        self.assertEqual(abi["request_templates"], 4)
        self.assertEqual(abi["mspi_handle"], "0x20074510")
        self.assertEqual(abi["framebuffer"], "0x20074514")
        self.assertEqual(abi["clear_callback"], "0x20074518")
        self.assertEqual(abi["command_scratch"], "0x2007451c")
        self.assertEqual(abi["operations_callbacks"], 15)

    def test_display_protocol(self) -> None:
        display = self.report["display"]
        self.assertEqual((display["width"], display["height"]), (640, 480))
        self.assertEqual(display["bits_per_pixel"], 4)
        self.assertEqual(display["scanline_bytes"], 320)
        self.assertEqual(display["offset_saturation"], 16)
        self.assertEqual(display["chip_id_value"], "0x01")
        self.assertEqual(display["status_62"], ["0x77", "0x57"])
        self.assertEqual(display["mirror_d8_mask"], "0x20")
        self.assertEqual(display["configuration_bytes"], 50)
        self.assertTrue(display["set_current_is_stub"])
        self.assertTrue(display["set_mode_is_stub"])

    def test_remains_analysis_only(self) -> None:
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
