import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_kvdb_als_scale.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_kvdb_als_scale", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2KvdbAlsScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 3,
            "body_bytes": 338,
            "physical_bytes": 388,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 21,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        })

    def test_record_and_migration(self) -> None:
        self.assertEqual(self.report["record"]["initialized_crc16"], "0xAA2D")
        self.assertEqual(self.report["record"]["schema_version"], 1)
        self.assertFalse(self.report["behavior"]["migration_imports_stored_record"])
        self.assertTrue(self.report["behavior"]["pre_v1_crc_mismatch_rewrites_current"])
        self.assertFalse(self.report["behavior"]["v1_crc_mismatch_rewrites_current"])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
