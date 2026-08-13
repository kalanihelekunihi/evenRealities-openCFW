import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_eat_registry.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_eat_registry", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2EatRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_registry_is_complete(self) -> None:
        self.assertEqual(self.report["registry"], {
            "interval": "[0x006c9260,0x006c93b0)",
            "bytes": 336,
            "record_size": 16,
            "registered_commands": 21,
            "unassigned_commands": 0,
            "valid_records_elsewhere": 0,
        })

    def test_all_records_are_assigned(self) -> None:
        self.assertEqual(sum(self.report["modules"].values()), 21)
        self.assertEqual(self.report["modules"]["g2-eat-core-sensor"], 12)
        self.assertEqual(self.report["commands"][0], "AT^CLEANBOND")
        self.assertEqual(self.report["commands"][-1], "AT^TP")

    def test_production_boundary(self) -> None:
        production = self.report["production"]
        self.assertEqual(production["production_routed_commands"], 0)
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["historical_source_inventory_complete"])


if __name__ == "__main__":
    unittest.main()
