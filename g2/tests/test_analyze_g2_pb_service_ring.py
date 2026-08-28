import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_ring.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_ring", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceRingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 4,
            "body_bytes": 1362,
            "owned_tail_bytes": 150,
            "physical_bytes": 1512,
            "direct_bl_entry_sites": 3,
            "stored_exact_entry_pointers": 1,
            "direct_body_calls": 82,
            "strict_interior_ingress": 0,
            "false_halfword_bl_candidates": 1,
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
        self.assertEqual(
            [contract["command_id"], contract["nested_payload_tag"], contract["relay_event_type"]],
            [1, 3, 0],
        )
        self.assertEqual([contract["route"], contract["service"]], [1, "0x91"])
        self.assertEqual(contract["message_bytes"], 0x40)
        self.assertEqual(contract["ring_mac_max_copied"], 6)
        self.assertEqual(contract["event_id_supported"], 1)

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("pb_service_ring.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 3)
        self.assertEqual(len(lineage["exact_symbols"]), 4)
        self.assertEqual(lineage["relay_registry_record"], "0x006a45b0")
        production = self.report["production"]
        self.assertEqual(
            production["candidate"],
            "components/apollo_main/core_overlay/pb_service_ring.c",
        )
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 1362)
        self.assertTrue(production["source_inventory_available"])
        self.assertEqual(production["source_functions"], 5)
        self.assertEqual(production["compiled_text_bytes"], 594)
        self.assertEqual(production["alignment_bytes"], 4)
        self.assertEqual(production["strict_relocations"], 9)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
