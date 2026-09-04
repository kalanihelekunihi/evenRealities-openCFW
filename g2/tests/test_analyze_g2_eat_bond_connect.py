import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_eat_bond_connect.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_eat_bond_connect", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2EatBondConnectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 2,
            "body_bytes": 34,
            "owned_noncode_bytes": 10,
            "physical_bytes": 44,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 4,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        })

    def test_command_contracts(self) -> None:
        clean, keep = self.report["commands"]
        self.assertEqual(clean["name"], "AT^CLEANBOND")
        self.assertEqual(clean["provider"], "0x004b46ce")
        self.assertEqual(clean["return_value"], 0)
        self.assertEqual(keep["name"], "AT^BLE_KEEPCONNECT")
        self.assertEqual(keep["record_type"], 1)
        self.assertEqual(keep["provider"], "0x0046f2dc")
        self.assertEqual(keep["provider_argument"], 1)
        self.assertEqual(keep["return_value"], 0)

    def test_lineage_and_production_boundary(self) -> None:
        self.assertIsNone(self.report["lineage"]["retained_path"])
        self.assertFalse(self.report["lineage"]["source_partition_known"])
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/eat_bond_connect.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 34)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 2)
        self.assertEqual(production["compiled_text_bytes"], {
            "apple-clang": 46,
            "linux-clang": 46,
        })
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])
        self.assertEqual(len(production["hardware_evidence_required"]), 2)


if __name__ == "__main__":
    unittest.main()
