import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_ux_battery_sync.py"
S = importlib.util.spec_from_file_location("g2_ux_battery_sync", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2UxBatterySyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_callback_and_physical_surface(self):
        s = self.report["surface"]
        self.assertEqual(
            (s["linked_functions"], s["path_anchored_functions"],
             s["body_bytes"], s["physical_bytes"], s["outer_pool_bytes"],
             s["reachable_instructions"], s["direct_body_calls"],
             s["indirect_body_calls"], s["direct_bl_entry_sites"],
             s["stored_entry_pointers"]),
            (1, 1, 836, 920, 84, 341, 57, 0, 0, 1),
        )

    def test_six_message_protocol(self):
        b = self.report["behavior"]
        self.assertEqual(b["minimum_message_bytes"], 12)
        self.assertEqual(b["service_record_id"], 0x105)
        self.assertEqual(b["accepted_message_ids"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(b["ring_level_clamp"], [0, 100])
        self.assertTrue(b["callbacks_only_on_change"])

    def test_no_hidden_rtos_or_new_third_party_definition(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (p["easylogger_calls"], p["g2_charger_common_calls"],
             p["g2_ring_battery_calls"], p["g2_callback_manager_calls"],
             p["direct_cmsis_freertos_calls"]),
            (45, 4, 6, 2, 0),
        )
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(p["new_version_discriminator"])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
