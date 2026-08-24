import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_dev_setting.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_dev_setting", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceDevSettingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 10, "body_bytes": 3432,
            "owned_gap_pool_bytes": 284, "physical_bytes": 3716,
            "assertion_records": 20, "direct_bl_entry_sites": 10,
            "direct_body_calls": 222, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 1,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {"success": 0, "null": 2})
        self.assertEqual(contract["tx_status"], {
            "success": 0, "null": 2, "encode_failure": 0x2B,
        })
        self.assertEqual(list(contract["commands"]), [0x0D, 0x0E, 0x0F, 0x80, 0x81])
        self.assertEqual([contract["route"], contract["service"]], [1, 0x80])
        self.assertEqual(contract["time_sync_bytes"], 5)

    def test_lineage_and_production_closure(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_dev_setting.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 22)
        self.assertEqual(len(lineage["exact_symbols"]), 10)
        self.assertEqual(len(lineage["assertion_lines"]), 20)
        production = self.report["production"]
        self.assertTrue(production["candidate"].endswith(
            "pb_service_dev_setting.c"
        ))
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 3432)
        self.assertEqual(production["source_functions"], 12)
        self.assertEqual(production["compiled_text_bytes"], 934)
        self.assertEqual(production["alignment_bytes"], 6)
        self.assertEqual(production["strict_relocations"], 30)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")


if __name__ == "__main__":
    unittest.main()
