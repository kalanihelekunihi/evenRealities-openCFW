import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_callback_manager.py"
S = importlib.util.spec_from_file_location("g2_callback_manager", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2CallbackManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report = M.analyze()

    def test_complete_object_with_restored_deinit(self):
        s = self.report["surface"]
        self.assertEqual(
            (s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"],
             s["body_bytes"],s["physical_bytes"],s["noncode_bytes"],
             s["reachable_instructions"],s["direct_body_calls"],
             s["internal_direct_body_calls"],s["external_direct_body_calls"],
             s["indirect_body_calls"],s["direct_bl_entry_sites"]),
            (8,7,1,1240,1360,120,506,76,4,72,1,23),
        )

    def test_list_and_notification_contract(self):
        b = self.report["behavior"]
        self.assertEqual((b["manager_record_bytes"],b["node_bytes"],b["count_field_bytes"]),(12,8,1))
        self.assertTrue(b["duplicate_registration_returns_success"])
        self.assertEqual(b["list_insertion"],"prepend")
        self.assertTrue(b["deinit_frees_all_nodes"] and b["null_callbacks_skipped"])
        self.assertEqual((b["notify_dynamic_call_site"],b["notify_arguments"]),("0x005105E4",2))

    def test_all_reusable_edges_are_admitted(self):
        p = self.report["provider_boundary"]
        self.assertEqual((p["easylogger_calls"],p["source_owned_heap_wrapper_calls"],p["direct_cmsis_freertos_calls"],p["bounded_registered_callback_sites"]),(70,2,0,1))
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[])
        self.assertFalse(p["new_version_discriminator"])

    def test_production_source_closure(self):
        p = self.report["production"]
        self.assertTrue(p["production_routed"] and p["source_inventory_available"])
        self.assertFalse(p["software_functional_gap"])
        self.assertEqual(
            (p["source_functions"], p["compiled_text_bytes"], p["alignment_bytes"],
             p["strict_relocations"], p["stock_replaced_bytes"],
             p["retained_diagnostic_pool_bytes"], p["hardware_validation"]),
            (8, 408, 14, 6, 1240, 118, "not-applicable"),
        )


if __name__ == "__main__": unittest.main()
