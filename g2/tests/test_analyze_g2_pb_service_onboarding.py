import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_onboarding.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_onboarding", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceOnboardingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 9, "body_bytes": 3024,
            "owned_gap_pool_bytes": 192, "physical_bytes": 3216,
            "assertion_records": 8, "direct_bl_entry_sites": 9,
            "direct_body_calls": 181, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 3,
        })

    def test_onboarding_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "command_or_handler_failure": 1,
            "null": 2, "decode_failure": 0x2B,
        })
        self.assertEqual(contract["tx_status"], {
            "success": 0, "null": 2, "encode_failure": 0x2B,
        })
        self.assertEqual(list(contract["commands"]), [1, 2, 3])
        self.assertEqual([contract["route"], contract["service"]], [1, 0x10])
        self.assertEqual([contract["message_bytes"], contract["encode_capacity"]],
                         [0x10, 0x100])
        self.assertEqual(contract["heartbeat_states"], {"ready": 0, "not_ready": 8})

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_onboarding.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 9)
        self.assertEqual(len(lineage["exact_symbols"]), 9)
        self.assertEqual(lineage["assertion_lines"],
                         [103, 117, 152, 188, 201, 240, 254, 294])
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_onboarding.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 3024)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 12)
        self.assertEqual(production["compiled_text_bytes"], 878)
        self.assertEqual(production["alignment_bytes"], 8)
        self.assertEqual(production["strict_relocations"], 22)
        self.assertEqual(production["stock_replaced_bytes"], 3024)
        self.assertEqual(production["retained_gap_pool_bytes"], 192)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")
        self.assertIn("deferred by project direction",
                      production["hardware_blocker"])


if __name__ == "__main__":
    unittest.main()
