import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_kvdb_module_configure.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_kvdb_module_configure", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2KvdbModuleConfigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 6,
            "body_bytes": 2286,
            "physical_bytes": 2492,
            "direct_bl_ingress_sites": 3,
            "direct_provider_calls": 115,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 8,
        })

    def test_scalar_records(self) -> None:
        self.assertEqual(self.report["scalars"]["language"]["accepted_values"], "0..7")
        self.assertEqual(self.report["scalars"]["language"]["default"], 0)
        self.assertEqual(self.report["scalars"]["dashboard_auto_close"]["default"], 10)
        self.assertTrue(
            self.report["scalars"]["dashboard_auto_close"]["mode_two_skips_read"]
        )

    def test_menu_abi_and_edge_cases(self) -> None:
        self.assertEqual(self.report["menu"]["record_bytes"], 888)
        self.assertEqual(self.report["menu"]["stored_item_bytes"], 44)
        self.assertEqual(self.report["menu"]["runtime_item_bytes"], 52)
        self.assertFalse(self.report["menu"]["stock_count_clamp"])
        self.assertFalse(self.report["menu"]["custom_text_copy_adds_terminator"])
        self.assertTrue(self.report["menu"]["writer_skips_identical_record"])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
