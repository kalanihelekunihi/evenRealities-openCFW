import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_glasses_case.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_glasses_case", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceGlassesCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 4,
            "body_bytes": 1360,
            "owned_pool_bytes": 124,
            "physical_bytes": 1484,
            "direct_bl_entry_sites": 4,
            "direct_body_calls": 86,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 6,
        })

    def test_message_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["rx_status"], {
            "success": 0, "unsupported_or_invalid": 1,
            "null": 2, "decode_failure": 0x2B,
        })
        self.assertEqual(contract["tx_status"], {
            "success": 0, "null": 2, "encode_failure": 0x2B,
        })
        self.assertEqual([contract["command_id"], contract["nested_payload_tag"]], [1, 3])
        self.assertEqual([contract["route"], contract["service"]], [1, "0x81"])
        self.assertEqual(contract["message_bytes"], 10)
        self.assertEqual(contract["encode_capacity"], 0x100)
        self.assertEqual(contract["case_info_bytes"], [
            "battery", "charging", "lid", "glasses_present", "error",
        ])

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_glasses_case.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 4)
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_glasses_case.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 1360)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 5)
        self.assertEqual(production["compiled_text_bytes"], 546)
        self.assertEqual(production["alignment_bytes"], 10)
        self.assertEqual(production["strict_relocations"], 16)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
