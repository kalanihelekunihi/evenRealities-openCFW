import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_algo.py"
S = importlib.util.spec_from_file_location("g2_service_algo", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceAlgoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["raw_path_references"], s["raw_path_referencing_functions"],
                s["body_bytes"], s["physical_bytes"], s["outer_pool_bytes"],
                s["reachable_instructions"],
            ),
            (10, 10, 10, 2, 3, 2, 1712, 1848, 136, 574),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (43, 12, 31, 0, 15, 0),
        )

    def test_signal_contract_and_short_input_policy(self):
        b = self.report["behavior"]
        self.assertEqual(b["stereo_frame_count"], 800)
        self.assertEqual(b["required_input_bytes"], 3200)
        self.assertTrue(b["stock_short_aligned_input_is_accepted_but_read_as_3200_bytes"])
        self.assertTrue(b["production_short_input_rejected"])
        self.assertEqual((b["correlation_lag_min"], b["correlation_lag_max"]), (-10, 10))
        self.assertEqual(b["rolling_energy_windows"], 10)
        self.assertEqual(b["angle_output_unit"], "signed degrees")

    def test_provider_accounting_and_math_identification(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_and_compact_calls"], p["iar_dlib_memory_math_calls"],
                p["source_owned_unsigned_64_division_calls"],
                p["iar_memset_calls"], p["iar_asin_calls"],
                p["iar_signed_64_to_double_calls"], p["iar_sqrt_calls"],
            ),
            (15, 10, 6, 3, 1, 4, 2),
        )
        self.assertFalse(self.report["identity"]["nationalchip_lvp_code_linked"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_route_and_physical_blocker(self):
        p = self.report["production"]
        self.assertTrue(p["source_admitted"])
        self.assertTrue(p["production_routed"])
        self.assertFalse(p["software_functional_gap"])
        self.assertEqual(p["source_functions"], 10)
        self.assertEqual((p["compiled_text_bytes"], p["linux_compiled_text_bytes"]), (4762, 4774))
        self.assertEqual((p["generated_alignment_bytes"], p["linux_generated_alignment_bytes"]), (14, 12))
        self.assertEqual(p["strict_relocations"], 20)
        self.assertEqual(p["guarded_redirects"], 10)
        self.assertEqual(p["functionally_displaced_stock_body_bytes"], 1712)
        self.assertEqual(p["manifest_changed_entry_bytes"], 40)
        self.assertEqual(p["physically_retained_compatibility_bytes"], 1808)
        self.assertEqual(p["retained_literal_pool_bytes"], 136)
        self.assertEqual(p["hardware_validation"], "blocked by unavailable physical evidence")


if __name__ == "__main__":
    unittest.main()
