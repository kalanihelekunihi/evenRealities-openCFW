import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_chg_bq25180.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_chg_bq25180", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ChgBq25180Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface_is_fully_closed(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 28,
            "body_bytes": 2268,
            "owned_pool_bytes": 116,
            "physical_bytes": 2384,
            "direct_bl_entry_sites": 56,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 93,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        })

    def test_stock_abi(self) -> None:
        self.assertEqual(self.report["abi"]["i2c_bus"], 7)
        self.assertEqual(self.report["abi"]["i2c_address"], "0x6a")
        self.assertEqual(self.report["abi"]["runtime_event_offset"], "0x14")
        self.assertEqual(self.report["abi"]["runtime_state_offset"], "0x16")

    def test_defaults_are_exact(self) -> None:
        self.assertEqual(self.report["defaults"]["call_count"], 19)
        self.assertEqual(
            self.report["defaults"]["register_image_hex"],
            "0000005a24241f4406002100f0",
        )
        self.assertTrue(self.report["defaults"]["charger_enabled_at_exit"])

    def test_candidate_is_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 1792)
        self.assertEqual(production["retained_stock_noncode_bytes"], 116)
        self.assertEqual(production["retained_stock_dead_body_bytes"], 476)
        self.assertEqual(len(production["relocated_leaves"]), 22)
        self.assertEqual(len(production["patch_sites"]), 22)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(
            production["bound_providers"],
            {
                "open_cfw_bq25180_bus_read": "0x0050436e",
                "open_cfw_bq25180_bus_write": "0x005044b4",
                "memset": "0x0043c0e4",
            },
        )


if __name__ == "__main__":
    unittest.main()
