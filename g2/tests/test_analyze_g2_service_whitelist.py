import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_service_whitelist.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_service_whitelist", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ServiceWhitelistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_linked_object_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_path_anchors": 5,
            "restored_pathless_functions": 2,
            "linked_functions": 7,
            "body_bytes": 4310,
            "owned_gap_pool_bytes": 418,
            "physical_bytes": 4728,
            "direct_bl_entry_sites": 9,
            "external_direct_bl_entry_sites": 5,
            "direct_body_calls": 264,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "b_w_entry_or_interior_targets": 0,
            "raw_instruction_windows": 1,
        })

    def test_whitelist_layout_and_policy(self) -> None:
        contract = self.report["contracts"]
        self.assertEqual(contract["state_bytes"], 8002)
        self.assertEqual(contract["application_limit"], 100)
        self.assertEqual(contract["application_stride"], 80)
        self.assertEqual(contract["application_id_bytes"], 64)
        self.assertEqual(contract["application_name_bytes"], 16)
        self.assertEqual(contract["flag_bits"]["application"], 4)
        self.assertEqual(contract["result_invalid"], 0)
        self.assertEqual(contract["result_blocked"], 1)
        self.assertEqual(contract["result_allowed"], 2)
        self.assertEqual(contract["disabled_policy"], "allow")
        self.assertEqual(
            contract["built_in_identifiers"], ["com.even.sg", "com.even.g1"]
        )

    def test_lineage_and_production_boundary(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["retained_path"].endswith("service_whitelist.c"))
        self.assertEqual(len(lineage["path_pointer_cells"]), 2)
        self.assertEqual(len(lineage["exact_symbols"]), 5)
        self.assertIn("SVC_WhitelistManagerInit", lineage["exact_symbols"])
        self.assertEqual(lineage["source_inventory"], "unavailable")
        self.assertEqual(lineage["license"], "unknown")
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
