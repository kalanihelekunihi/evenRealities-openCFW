import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_eat_core_sensor.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_eat_core_sensor", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2EatCoreSensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 12,
            "body_bytes": 486,
            "owned_noncode_bytes": 126,
            "physical_bytes": 612,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 49,
            "stored_entry_pointers": 12,
            "strict_interior_ingress": 0,
        })

    def test_command_table_and_product_identity(self) -> None:
        self.assertEqual([item["name"] for item in self.report["commands"]], [
            "AT^INFO", "AT^RESET", "AT^PSN", "AT^IMU_RAWDATA",
            "AT^IMU_EULER", "AT^SCRN_X", "AT^SCRN_Y", "AT^ALS_READ",
            "AT^ALS", "AT^BRIGHTNESS", "AT^ALS_SCALE_READ",
            "AT^BRIGHTNESS_READ",
        ])
        self.assertEqual(self.report["product"], {
            "name": "S200",
            "software": "2.2.6.10",
            "compile_date": "Jul  6 2026",
            "compile_time": "21:37:47",
        })

    def test_stock_contract_quirks(self) -> None:
        contracts = self.report["contracts"]
        self.assertEqual(contracts["psn_required_length"], 14)
        self.assertEqual(contracts["imu_raw_values"], [0, 1])
        self.assertEqual(contracts["screen_y_machine_range"], [0, 192])
        self.assertEqual(contracts["screen_y_diagnostic_range"], [1, 192])
        self.assertTrue(contracts["als_other_values_acknowledged"])
        self.assertTrue(contracts["brightness_unvalidated"])
        self.assertEqual(contracts["lux_base_address"], "0x200039bc")

    def test_lineage_and_production_boundary(self) -> None:
        self.assertIsNone(self.report["lineage"]["retained_path"])
        self.assertFalse(self.report["lineage"]["source_partition_known"])
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
