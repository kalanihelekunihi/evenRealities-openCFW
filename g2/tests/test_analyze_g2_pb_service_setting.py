import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_setting.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_setting", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceSettingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface_and_missed_bodies(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 11, "body_bytes": 3466,
            "owned_gap_pool_bytes": 334, "physical_bytes": 3800,
            "direct_bl_entry_sites": 23, "direct_body_calls": 221,
            "stored_exact_entry_pointers": 0, "strict_interior_ingress": 0,
            "raw_instruction_windows": 13, "manually_restored_bodies": 2,
        })

    def test_setting_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["parse_status"], {
            "accepted": 1, "rejected_or_duplicate": 0,
        })
        self.assertEqual(contract["serializer_status"], {
            "success_or_not_master": 0, "invalid_command_or_null": 1,
            "encode_failure": 0x2B,
        })
        self.assertEqual([contract["route"], contract["service"]], [1, 9])
        self.assertEqual([contract["message_bytes"], contract["encode_capacity"]],
                         [0x68, 0x100])
        self.assertEqual(contract["full_status"], {"command": 2, "tag": 4})
        self.assertEqual(contract["status_notifications"]["recalibration"]["selector"], 1)
        self.assertEqual(contract["status_notifications"]["silent_mode"]["selector"], 2)

    def test_lineage_and_production_closure(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_setting.c"))
        self.assertEqual(lineage["path_pointer_cells"],
                         ["0x0049bbbc", "0x0049c028"])
        self.assertEqual(len(lineage["exact_symbols"]), 11)
        production = self.report["production"]
        self.assertTrue(production["candidate"].endswith("pb_service_setting.c"))
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 3466)
        self.assertEqual(production["source_functions"], 13)
        self.assertEqual(production["compiled_text_bytes"], 1650)
        self.assertEqual(production["alignment_bytes"], 14)
        self.assertEqual(production["strict_relocations"], 38)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")


if __name__ == "__main__":
    unittest.main()
