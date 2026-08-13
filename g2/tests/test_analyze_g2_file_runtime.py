import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_file_runtime.py"
S = importlib.util.spec_from_file_location("g2_file_runtime", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2FileRuntimeTests(unittest.TestCase):
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
                s["body_bytes"], s["physical_bytes"], s["data_bytes"],
                s["reachable_instructions"],
            ),
            (18, 18, 0, 5, 9, 5, 2266, 2404, 138, 864),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (132, 8, 124, 0, 644, 3),
        )

    def test_provider_accounting_and_commits(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["cmsis_freertos_calls"], p["easylogger_and_compact_calls"],
                p["production_owned_errno_log_calls"], p["iar_dlib_calls"],
                p["littlefs_backend_adapter_calls"], p["tlsf_calls"],
                p["first_party_assert_calls"],
            ),
            (36, 30, 32, 6, 14, 3, 3),
        )
        self.assertEqual(p["cmsis_freertos_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
        self.assertEqual(p["littlefs_commit"], "0494ce7169f06a734a7bd7585f49a9fa91fa7318")
        self.assertEqual(p["tlsf_commit"], "deff9ab509341f264addbd3c8ada533678591905")
        self.assertEqual(p["embedded_third_party_definitions"], 0)

    def test_all_linked_functions_are_production_source_owned(self):
        p = self.report["production"]
        self.assertTrue(p["production_routed"])
        self.assertEqual(p["source_owned_functions"], 18)
        self.assertEqual(len(p["source_owned_function_entries"]), 18)


if __name__ == "__main__":
    unittest.main()
