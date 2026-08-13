import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_kvdb_onboarding_config.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_kvdb_onboarding_config", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2KvdbOnboardingConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 6,
            "body_bytes": 286,
            "physical_bytes": 340,
            "direct_bl_ingress_sites": 18,
            "direct_provider_calls": 20,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        })

    def test_record_and_behavior(self) -> None:
        self.assertEqual(self.report["record"]["address"], "0x20000040")
        self.assertEqual(self.report["record"]["boot_hex"], "00")
        self.assertFalse(self.report["record"]["has_version"])
        self.assertFalse(self.report["record"]["has_crc"])
        self.assertTrue(self.report["behavior"]["read_imports_stored_byte"])
        self.assertTrue(self.report["behavior"]["pointer_getter_ignores_index"])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
