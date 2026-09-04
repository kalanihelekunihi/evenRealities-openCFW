import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_at_nus.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_at_nus", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2AtNusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 1,
            "body_bytes": 12,
            "owned_noncode_bytes": 4,
            "physical_bytes": 16,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 1,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        })

    def test_command_contract(self) -> None:
        self.assertEqual(self.report["command"], {
            "name": "AT^NUS",
            "handler": "atNusHandler",
            "record_type": 0,
            "response": "NUS+OK\\r\\n",
            "output_provider": "0x00541430",
            "return_value": 1,
        })

    def test_lineage_and_production_boundary(self) -> None:
        self.assertIsNone(self.report["lineage"]["retained_path"])
        self.assertIsNone(self.report["lineage"]["exact_historical_symbol"])
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/at_nus.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 16)
        self.assertTrue(production["source_inventory_available"])
        self.assertFalse(production["historical_source_inventory_available"])
        self.assertEqual(
            production["toolchain_profiles"], ["apple-clang", "linux-clang"]
        )
        self.assertEqual(
            production["relocated_leaves"], [
                "open_cfw_at_nus_handler",
                "open_cfw_at_nus_handler_linux",
            ]
        )
        self.assertEqual(production["patch_sites"], [
            "replace_at_nus_handler_apple",
            "replace_at_nus_handler_linux",
        ])
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])
        self.assertEqual(len(production["hardware_evidence_required"]), 1)


if __name__ == "__main__":
    unittest.main()
