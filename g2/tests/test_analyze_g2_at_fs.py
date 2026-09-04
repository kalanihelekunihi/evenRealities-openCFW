import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_at_fs.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_at_fs", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2AtFsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 4,
            "body_bytes": 416,
            "owned_noncode_bytes": 80,
            "physical_bytes": 496,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 33,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
        })

    def test_command_contract(self) -> None:
        commands = self.report["commands"]
        self.assertEqual(commands["names"], ["AT^RM", "AT^LS", "AT^MKDIR"])
        self.assertEqual(commands["record_type"], 3)
        self.assertEqual(commands["filesystem_ready_global"], "0x200746a8")
        self.assertEqual(commands["filesystem_ready_value"], 1)
        self.assertEqual(commands["list_skips"], [".", ".."])
        self.assertEqual(commands["file_size_units"], ["bytes", "integer KiB"])

    def test_lineage_and_production_boundary(self) -> None:
        self.assertEqual(self.report["lineage"]["exact_symbol"], "_atRM")
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/at_fs.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 48)
        self.assertEqual(production["changed_flash_bytes"], 9)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 4)
        self.assertEqual(
            production["compiled_text_bytes"],
            {"apple-clang": 458, "linux-clang": 456},
        )
        self.assertEqual(production["command_record_bytes_replaced"], 48)
        self.assertEqual(production["stock_body_bytes_superseded_by_lc3_host"], 416)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])


if __name__ == "__main__":
    unittest.main()
