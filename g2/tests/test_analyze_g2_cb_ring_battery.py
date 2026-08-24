import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_cb_ring_battery.py"
S = importlib.util.spec_from_file_location("g2_cb_ring_battery", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2CbRingBatteryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_pathless_census_item_is_a_complete_five_function_object(self):
        s = self.report["surface"]
        self.assertEqual(
            (s["linked_functions"], s["ghidra_discovered_functions"],
             s["restored_functions"], s["path_anchored_functions"],
             s["body_bytes"], s["physical_bytes"],
             s["outer_pool_and_alignment_bytes"], s["reachable_instructions"],
             s["direct_bl_entry_sites"]),
            (5, 1, 4, 1, 122, 152, 30, 50, 6),
        )

    def test_callback_facade_contract(self):
        b = self.report["behavior"]
        self.assertEqual(b["callback_list_address"], 0x20073F90)
        self.assertEqual(b["callback_type"], "RING_BAT_INFO")
        self.assertTrue(b["has_init"] and b["has_deinit"])
        self.assertTrue(b["null_registration_rejected"])
        self.assertEqual(b["notification_keys_observed_from_battery_sync"], [0, 1])

    def test_only_easylogger_is_third_party(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (p["easylogger_calls"], p["g2_ring_battery_consumer_calls"],
             p["g2_generic_callback_manager_calls"],
             p["direct_cmsis_freertos_calls"]),
            (5, 1, 4, 0),
        )
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(p["new_version_discriminator"])

    def test_production_routed_without_a_hardware_gap(self):
        p = self.report["production"]
        self.assertEqual(
            (p["production_routed"], p["source_functions"],
             p["compiled_text_bytes"], p["alignment_bytes"],
             p["strict_relocations"], p["stock_replaced_bytes"],
             p["retained_diagnostic_pool_bytes"],
             p["software_functional_gap"], p["hardware_validation"]),
            (True, 5, 88, 2, 5, 122, 30, False, "not-applicable"),
        )


if __name__ == "__main__":
    unittest.main()
