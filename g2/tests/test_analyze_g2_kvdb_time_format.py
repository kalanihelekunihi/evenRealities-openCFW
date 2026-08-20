import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_kvdb_time_format.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_kvdb_time_format", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2KvdbTimeFormatTests(unittest.TestCase):
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
        self.assertEqual(self.report["record"]["initialized_crc16"], "0x76ED")
        self.assertEqual(self.report["record"]["crc_offset"], 8)
        self.assertFalse(self.report["behavior"]["migration_imports_stored_record"])
        self.assertFalse(self.report["behavior"]["v1_crc_mismatch_rewrites_current"])

    def test_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 338)
        self.assertEqual(production["retained_stock_tail_bytes"], 50)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(production["relocated_leaves"], [
            "open_cfw_kvdb_time_format_default_initialize",
            "open_cfw_kvdb_time_format_load_and_migrate",
            "open_cfw_kvdb_write_time_format",
        ])
        self.assertEqual(production["patch_sites"], [
            "replace_kvdb_time_format_default_initialize",
            "replace_kvdb_time_format_load_and_migrate",
            "replace_kvdb_write_time_format",
        ])


if __name__ == "__main__":
    unittest.main()
