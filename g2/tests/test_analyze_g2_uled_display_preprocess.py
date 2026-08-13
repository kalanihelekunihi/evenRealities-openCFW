import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_uled_display_preprocess.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_uled_display_preprocess", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2UledDisplayPreprocessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 1,
            "body_bytes": 584,
            "owned_pool_bytes": 64,
            "object_bytes": 648,
            "direct_bl_ingress_sites": 1,
            "direct_provider_calls": 23,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 2,
        })

    def test_abi(self) -> None:
        self.assertEqual(self.report["abi"]["destination_descriptor_bytes"], 28)
        self.assertEqual(self.report["abi"]["source_region_bytes"], 16)
        self.assertEqual(self.report["abi"]["destination_control"], "0x00000619")
        self.assertEqual(self.report["abi"]["pointer_alignment"], 8)
        self.assertEqual(self.report["abi"]["source_format"], 9)

    def test_preconditions_and_result_gate(self) -> None:
        self.assertEqual(len(self.report["behavior"]["preconditions"]), 9)
        self.assertEqual(self.report["behavior"]["gpu_success_value"], 1)
        self.assertTrue(self.report["behavior"]["gpu_failure_diagnoses_and_returns"])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
