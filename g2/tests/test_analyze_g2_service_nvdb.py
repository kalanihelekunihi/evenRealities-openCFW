import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_nvdb.py"
S = importlib.util.spec_from_file_location("g2_service_nvdb", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceNvdbTests(unittest.TestCase):
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
            (5, 5, 3, 2, 8, 2, 930, 1052, 122, 379),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (60, 3, 57, 0, 20, 0),
        )

    def test_factory_database_and_reset_contract(self):
        b = self.report["behavior"]
        self.assertEqual((b["database_index"], b["database_name"], b["partition_name"]), (1, "factory", "NVdb"))
        self.assertEqual((b["partition_offset"], b["partition_bytes"]), (0x01FF8000, 0x8000))
        self.assertEqual((b["default_table_address"], b["default_node_count"]), ("0x20003868", 9))
        self.assertEqual((b["factory_magic_key"], b["factory_magic_value"]), ("nvMagic", 0x55550022))
        self.assertEqual(b["stock_magic_mismatch_policy"], "wholesale fdb_kv_set_default")
        self.assertEqual(b["production_magic_mismatch_policy"], "fail closed without reset")
        self.assertTrue(b["stock_fal_zero_on_driver_failure_hazard"])

    def test_flashdb_provenance_and_provider_accounting(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_and_compact_calls"], p["iar_dlib_calls"],
                p["flashdb_core_calls"], p["g2_database_adapter_calls"],
                p["g2_serial_policy_calls"],
            ),
            (40, 2, 4, 9, 2),
        )
        self.assertEqual((p["flashdb_version"], p["flashdb_commit"]), ("2.1.1", "714d6159e7e6afb267a3953756abca445c350e61"))
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_routing_is_non_destructive_and_hardware_blocked(self):
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(
            (production["compiled_text_bytes"], production["alignment_bytes"],
             production["strict_relocations"], production["replaced_stock_body_bytes"],
             production["retained_official_pool_bytes"]),
            (514, 4, 11, 930, 122),
        )
        self.assertFalse(production["destructive_default_reset_enabled"])
        self.assertIn("deferred by project direction", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
