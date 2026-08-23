import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_watchdog.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_watchdog", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2WatchdogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 2,
            "body_bytes": 140,
            "owned_noncode_bytes": 32,
            "physical_bytes": 172,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 1,
            "direct_body_calls": 13,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        })

    def test_selector_contract(self) -> None:
        behavior = self.report["behavior"]
        self.assertTrue(behavior["init_calls_enable"])
        self.assertEqual(behavior["selector_provider"], "0x0050938e")
        self.assertEqual(behavior["selector_argument"], 0)
        self.assertEqual(behavior["required_selector_value"], 1)
        self.assertEqual(behavior["watchdog_enable_provider"], "0x00511882")

    def test_clean_room_candidate_is_production_routed(self) -> None:
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/watchdog.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 28)
        self.assertEqual(production["generated_replacement_bytes"], 140)
        self.assertEqual(production["retained_literal_pool_bytes"], 32)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
