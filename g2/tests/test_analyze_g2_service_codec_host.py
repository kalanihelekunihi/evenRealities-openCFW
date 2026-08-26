import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_service_codec_host.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_service_codec_host", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ServiceCodecHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 13,
            "restored_pathless_functions": 13,
            "linked_functions": 26,
            "body_bytes": 7318,
            "owned_gap_pool_bytes": 1314,
            "physical_bytes": 8632,
            "direct_bl_entry_sites": 83,
            "external_direct_bl_entry_sites": 25,
            "direct_body_calls": 379,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 1,
        })

    def test_protocol_contract(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["magic"], "BUXX")
        self.assertEqual(contract["uart_baud"], 115200)
        self.assertEqual(contract["wire_header_bytes"], 14)
        self.assertEqual(contract["header_crc_input_bytes"], 10)
        self.assertEqual(contract["body_max_bytes"], 16)
        self.assertEqual(contract["command_retry_limit"], 3)
        self.assertEqual(contract["known_commands"][0x0E], "microphone_delay_1bit")
        self.assertEqual(contract["known_commands"][0x70], "query_microphone_state")

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("service_codec_host.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 4)
        self.assertEqual(len(lineage["exact_symbols"]), 23)
        self.assertEqual(lineage["source_inventory"],
                         "26-function clean-room production C")
        self.assertEqual(lineage["historical_source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "GPL-3.0-only")
        production = self.report["production"]
        self.assertEqual(production["candidate"],
                         "components/apollo_main/core_overlay/service_codec_host.c")
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 7318)
        self.assertEqual(production["compiled_text_bytes"], 4262)
        self.assertEqual(production["generated_alignment_bytes"], 38)
        self.assertEqual(production["strict_relocations"], 111)
        self.assertEqual(production["guarded_redirects"], 26)
        self.assertEqual(production["hardware_validation"],
                         "blocked_unavailable_physical_evidence")


if __name__ == "__main__":
    unittest.main()
