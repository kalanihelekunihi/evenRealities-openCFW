import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_at_codec.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_at_codec", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2AtCodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 1,
            "body_bytes": 118,
            "owned_noncode_bytes": 34,
            "physical_bytes": 152,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 10,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        })

    def test_command_contract(self) -> None:
        command = self.report["command"]
        self.assertEqual(command["name"], "AT^AUDIO")
        self.assertEqual(command["handler"], "_atAudioCtrl")
        self.assertEqual(command["record_type"], 0)
        self.assertEqual(command["enable"], {
            "leading_character": "1", "provider": "0x0054f380", "selector": 7,
        })
        self.assertEqual(command["disable"], {
            "leading_character": "0", "provider": "0x0054f50e", "selector": 7,
        })
        self.assertEqual(command["response"], "AUD_AUDIO+OK\r\n")
        self.assertEqual(command["return_value"], 1)

    def test_lineage_and_production_boundary(self) -> None:
        self.assertEqual(self.report["lineage"]["exact_symbol"], "_atAudioCtrl")
        production = self.report["production"]
        self.assertEqual(production["candidate"], "components/apollo_main/core_overlay/at_codec.c")
        self.assertTrue(production["production_routed"])
        self.assertEqual((production["ownership_bytes"],
                          production["compiled_text_bytes"],
                          production["stock_replaced_bytes"],
                          production["retained_official_pool_bytes"],
                          production["strict_relocations"]), (162, 44, 118, 34, 3))
        self.assertTrue(production["source_inventory_available"])
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
