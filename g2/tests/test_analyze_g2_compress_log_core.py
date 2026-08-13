import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_compress_log_core.py"
S = importlib.util.spec_from_file_location("g2_compress_log_core", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2CompressLogCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_body_surface(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["raw_path_references"], s["raw_path_referencing_functions"],
                s["body_bytes"], s["reachable_instructions"],
                s["external_interleaved_literal_cells"],
                s["physical_interval_claimed"],
            ),
            (8, 7, 1, 2, 6, 3, 2300, 898, 23, False),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (78, 11, 67, 0, 5726, 0),
        )

    def test_compact_record_and_persistence_contract(self):
        self.assertEqual(
            self.report["behavior"],
            {
                "compact_record_bytes": 44,
                "compact_header_bytes": 12,
                "maximum_argument_bytes": 32,
                "string_tail_bytes": 16,
                "sync_period_ticks": 10000,
                "sync_block_bytes": 4096,
                "maximum_periodic_blocks": 9,
            },
        )

    def test_provider_accounting_and_easylogger_correction(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["iar_dlib_calls"], p["easylogger_control_output_calls"],
                p["freertos_kernel_port_calls"], p["cmsis_freertos_calls"],
                p["other_first_party_calls"],
            ),
            (13, 30, 14, 2, 8),
        )
        self.assertEqual(p["private_compact_output_entry"], "0x0043CE9E")
        self.assertEqual(p["upstream_derived_elog_output_entry"], "0x0043D574")
        self.assertFalse(p["private_hook_is_upstream_easylogger"])
        self.assertEqual(p["easylogger_commit"], "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24")
        self.assertEqual(p["cmsis_freertos_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
        self.assertEqual(p["freertos_kernel_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
