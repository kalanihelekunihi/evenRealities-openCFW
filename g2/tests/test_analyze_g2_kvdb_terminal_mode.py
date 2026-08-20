import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_kvdb_terminal_mode.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_kvdb_terminal_mode", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2KvdbTerminalModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 3,
            "body_bytes": 334,
            "physical_bytes": 384,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 21,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        })

    def test_record_and_migration(self) -> None:
        self.assertEqual(self.report["record"]["mode_offset"], 1)
        self.assertEqual(self.report["record"]["initialized_crc16"], "0x2E3E")
        self.assertFalse(self.report["behavior"]["migration_imports_stored_record"])
        self.assertTrue(self.report["behavior"]["v0_crc_mismatch_rewrites_current"])
        self.assertFalse(self.report["behavior"]["v1_crc_mismatch_rewrites_current"])

    def test_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 334)
        self.assertEqual(production["retained_stock_tail_bytes"], 50)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(production["relocated_leaves"], [
            "open_cfw_kvdb_terminal_mode_default_initialize",
            "open_cfw_kvdb_terminal_mode_load_and_migrate",
            "open_cfw_kvdb_write_terminal_mode",
        ])
        self.assertEqual(production["patch_sites"], [
            "replace_kvdb_terminal_mode_default_initialize",
            "replace_kvdb_terminal_mode_load_and_migrate",
            "replace_kvdb_write_terminal_mode",
        ])


if __name__ == "__main__":
    unittest.main()
