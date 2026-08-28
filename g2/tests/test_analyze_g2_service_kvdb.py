import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_kvdb.py"
S = importlib.util.spec_from_file_location("g2_service_kvdb", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceKvdbTests(unittest.TestCase):
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
                s["body_bytes"], s["physical_bytes"],
                s["outer_pool_and_alignment_bytes"], s["reachable_instructions"],
            ),
            (7, 7, 5, 2, 13, 2, 1384, 1540, 156, 550),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_call_sites"],
                s["bounded_indirect_target_entries"], s["direct_bl_entry_sites"],
                s["stored_entry_pointers"],
            ),
            (88, 4, 84, 1, 11, 32, 0),
        )

    def test_sysenv_schema_and_reset_policy(self):
        b = self.report["behavior"]
        self.assertEqual((b["database_index"], b["database_name"], b["partition_name"]), (0, "sysenv", "kvdb"))
        self.assertEqual((b["partition_offset"], b["partition_bytes"]), (0x1FC0000, 0x38000))
        self.assertEqual((b["default_table_address"], b["default_node_count"]), ("0x2000372c", 12))
        self.assertEqual((b["magic_key"], b["magic_value"]), ("kvMagic", 0x5A000020))
        self.assertEqual(b["stock_magic_mismatch_policy"], "wholesale fdb_kv_set_default")
        self.assertEqual(b["production_magic_mismatch_policy"], "fail closed without reset")
        self.assertEqual((b["lock_callback_command"], b["unlock_callback_command"]), (2, 3))
        self.assertEqual(b["migration_callbacks"], 11)

    def test_boot_counter_default_and_lifecycle_are_resolved(self):
        b = self.report["behavior"]
        self.assertEqual((b["boot_count_key"], b["boot_count_value_address"]), ("kvbooCount", "0x20074988"))
        self.assertEqual(b["boot_count_startup_value"], 0)
        self.assertEqual(b["boot_count_startup_zero_range"], ["0x20004558", "0x20075048"])
        self.assertTrue(b["boot_count_read_increment_write"])
        self.assertTrue(b["invalidate_magic_writes_zero"])

    def test_flashdb_and_first_party_provider_split(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_and_compact_calls"], p["iar_dlib_calls"],
                p["flashdb_core_calls"], p["g2_database_adapter_calls"],
                p["closed_onboarding_record_calls"],
                p["closed_migration_target_entries"],
            ),
            (65, 1, 4, 12, 2, 11),
        )
        self.assertEqual(p["flashdb_version"], "2.1.1")
        self.assertEqual(p["flashdb_commit"], "714d6159e7e6afb267a3953756abca445c350e61")
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_routing_is_non_destructive_and_hardware_blocked(self):
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(
            (production["compiled_text_bytes"], production["alignment_bytes"],
             production["strict_relocations"], production["replaced_stock_body_bytes"],
             production["retained_official_pool_bytes"]),
            (342, 8, 23, 1384, 156),
        )
        self.assertFalse(production["destructive_default_reset_enabled"])
        self.assertFalse(self.report["behavior"]["production_invalidate_magic_writes_zero"])
        self.assertIn("deferred by project direction", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
