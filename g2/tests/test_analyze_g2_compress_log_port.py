import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_compress_log_port.py"
S = importlib.util.spec_from_file_location("g2_compress_log_port", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2CompressLogPortTests(unittest.TestCase):
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
                s["body_bytes"], s["physical_bytes"], s["outer_data_bytes"],
                s["reachable_instructions"],
            ),
            (12, 11, 1, 3, 6, 4, 1324, 1464, 140, 526),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (68, 15, 53, 0, 23, 1),
        )

    def test_rotation_and_export_contract(self):
        self.assertEqual(
            self.report["behavior"],
            {
                "rotation_file_count": 5,
                "maximum_file_bytes": 512000,
                "manager_record_bytes": 12,
                "manager_magic": "0x4C4D4752",
                "version_header": "Software_Version: 2.2.6.10\n",
                "export_timeout_ticks": 120000,
            },
        )

    def test_provider_accounting_and_source_owned_shortcuts(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_control_output_calls"],
                p["closed_compact_log_core_calls"], p["iar_dlib_calls"],
                p["source_owned_file_runtime_calls"],
                p["source_owned_delayed_callback_calls"],
            ),
            (24, 6, 2, 18, 3),
        )
        self.assertTrue(p["all_file_runtime_entries_production_source_owned"])
        self.assertTrue(p["all_delayed_callback_entries_production_source_owned"])
        self.assertFalse(p["private_compact_hook_is_upstream_easylogger"])
        self.assertEqual(p["littlefs_version"], "v2.10.1-equivalent")
        self.assertEqual(p["littlefs_commit"], "0494ce7169f06a734a7bd7585f49a9fa91fa7318")
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
