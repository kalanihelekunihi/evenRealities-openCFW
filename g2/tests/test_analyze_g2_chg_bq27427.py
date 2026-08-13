import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_chg_bq27427.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_chg_bq27427", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ChgBq27427Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface_is_fully_closed(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 37,
            "body_bytes": 4440,
            "owned_noncode_bytes": 396,
            "physical_bytes": 4836,
            "direct_bl_entry_sites": 88,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 287,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        })

    def test_stock_bus_and_runtime_abi(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["i2c_bus"], 7)
        self.assertEqual(abi["i2c_address"], "0x55")
        self.assertEqual(abi["runtime_global"], "0x20073b18")
        self.assertEqual(abi["runtime_offsets"], {
            "soc": 4, "voltage": 8, "current": 12, "temperature": 16,
        })
        self.assertEqual(abi["unseal_key"], "0x80008000")

    def test_initialized_configuration_is_exact(self) -> None:
        config = self.report["configuration"]
        self.assertEqual(config["defaults"], [240, 80, 3100])
        self.assertEqual(len(config["descriptors"]), 7)
        self.assertEqual(config["descriptors"][0], {
            "subclass": 82,
            "offset": 6,
            "width": 2,
            "minimum": 0,
            "maximum": 8000,
        })
        self.assertEqual(config["descriptors"][6]["subclass"], 105)

    def test_candidate_remains_production_excluded(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
