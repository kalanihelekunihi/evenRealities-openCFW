import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_dev_config.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_dev_config", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceDevConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 3,
            "body_bytes": 2646,
            "owned_gap_pool_bytes": 286,
            "physical_bytes": 2932,
            "assertion_records": 1,
            "direct_bl_entry_sites": 3,
            "direct_body_calls": 172,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 2,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "null": 2, "decode_failure": 0x2B,
        })
        self.assertEqual(contract["decoded_message_bytes"], 0xD0)
        self.assertEqual(list(contract["commands"]), [
            4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 128, 129,
        ])
        self.assertEqual(contract["error_codes_logged"], [1, 5, 7, 8, 9])
        self.assertEqual(contract["unknown_command_error"], 8)
        self.assertEqual(contract["tx_status"], {
            "success": 0, "encode_failure": 0x2B,
        })
        self.assertEqual(
            [contract["tx_command"], contract["tx_tag"],
             contract["route"], contract["service"]],
            [10, 9, 1, 0x80],
        )
        self.assertEqual(contract["message_bytes"], 0xD0)
        self.assertEqual(contract["encode_capacity"], 0x100)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_dev_config.c"))
        self.assertEqual(lineage["path_pointer_cells"], [
            "0x004d8b84", "0x004d8eec", "0x00781974",
        ])
        self.assertEqual(len(lineage["exact_symbols"]), 3)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_dev_config.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 2646)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 5)
        self.assertEqual(production["compiled_text_bytes"], 998)
        self.assertEqual(production["alignment_bytes"], 4)
        self.assertEqual(production["strict_relocations"], 33)
        self.assertEqual(production["stock_replaced_bytes"], 2646)
        self.assertEqual(production["retained_gap_pool_bytes"], 286)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "blocked")
        self.assertIn("authorized right temple is nonresponsive",
                      production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
