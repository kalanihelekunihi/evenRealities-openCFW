import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_at_buzzer.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_at_buzzer", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2AtBuzzerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 1,
            "body_bytes": 1014,
            "owned_noncode_bytes": 194,
            "physical_bytes": 1208,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 76,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        })

    def test_command_contract(self) -> None:
        command = self.report["command"]
        self.assertEqual(command["name"], "AT^BUZZER")
        self.assertEqual(command["handler"], "_atBuzzerTest")
        self.assertEqual(command["record_type"], 2)
        self.assertEqual(command["subcommands"], ["note", "play", "start", "stop"])
        self.assertEqual(command["note_ranges"], {
            "note": [0, 7], "tone": [0, 3], "beat": [1, 100],
        })
        self.assertEqual(command["play_type_range"], [0, 10])
        self.assertEqual(command["start_ranges"], {
            "frequency_hz": [1, 20000], "duty_percent": [0, 100],
        })
        self.assertEqual(command["driver_targets"], {
            "note": "0x00502bf8",
            "play": "0x00502bf0",
            "start": "0x00502c88",
            "stop": "0x00502d4c",
        })

    def test_lineage_and_production_boundary(self) -> None:
        self.assertEqual(self.report["lineage"]["exact_symbol"], "_atBuzzerTest")
        self.assertEqual(self.report["lineage"]["command_record"], "[0x006c9280,0x006c9290)")
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/at_buzzer.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 3948)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 1)
        self.assertEqual(production["compiled_text_bytes"], 2740)
        self.assertEqual(production["alignment_bytes"], 0)
        self.assertEqual(production["stock_replaced_bytes"], 1208)
        self.assertEqual(production["strict_relocations"], 23)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")
        self.assertIn("required for future qualification", production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
