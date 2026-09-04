import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pdt_distortion_test.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pdt_distortion_test", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PdtDistortionTestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 4,
            "body_bytes": 850,
            "literal_pool_bytes": 46,
            "physical_bytes": 896,
            "descriptor_bytes": 16,
            "direct_bl_entry_sites": 4,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 83,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
        })

    def test_registration_and_behavior(self) -> None:
        registration = self.report["registration"]
        self.assertEqual(registration["screen_id"], "0x00000110")
        self.assertEqual(registration["data_handler"], "0x005cf2e7")
        self.assertEqual(registration["screen_event_handler"], "0x005cf331")
        self.assertEqual(registration["predicate"], "0x005cf32d")
        behavior = self.report["behavior"]
        self.assertEqual(behavior["construct_event"], 2)
        self.assertEqual(behavior["root_dimensions"], [640, 480])
        self.assertEqual(behavior["object_create_calls"], 4)

    def test_boundary_and_production_status(self) -> None:
        self.assertEqual(self.report["boundary"]["next_handler"], "0x005cf634")
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["source_functions"], 4)
        self.assertEqual(production["stock_body_bytes_displaced"], 850)
        self.assertEqual(production["ownership_bytes"], 850)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])
        self.assertEqual(production["hardware_evidence_required"], [
            "authorized G2 panel trace confirming the recovered 640x480 root, 574x206 frame at (0,50), nested flex layout, image asset, and both localized resource labels",
        ])


if __name__ == "__main__":
    unittest.main()
