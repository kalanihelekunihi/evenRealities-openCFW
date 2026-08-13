import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_audio_manager.py"
S = importlib.util.spec_from_file_location("g2_service_audio_manager", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceAudioManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface_and_restored_functions(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["raw_path_references"], s["raw_path_referencing_functions"],
                s["body_bytes"], s["physical_bytes"],
                s["outer_pool_and_alignment_bytes"], s["reachable_instructions"],
            ),
            (7, 5, 2, 4, 16, 6, 1554, 1728, 174, 595),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (112, 11, 101, 0, 38, 1),
        )

    def test_ownership_and_peer_handshake(self):
        b = self.report["behavior"]
        self.assertEqual(b["application_slots"], 8)
        self.assertEqual(b["valid_application_ids"], list(range(1, 8)))
        self.assertEqual(b["hardware_ownership_role"], 2)
        self.assertTrue(b["hardware_enabled_on_first_acquire"])
        self.assertTrue(b["hardware_disabled_on_last_release"])
        self.assertEqual((b["common_data_frame_id"], b["peer_message_ids"]), (0x10C, [1, 2, 3, 4]))
        self.assertTrue(b["peer_messages_are_role_sensitive"])

    def test_no_hidden_rtos_or_dsp_dependency(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_and_compact_calls"], p["iar_dlib_memset_calls"],
                p["g2_product_role_and_system_calls"],
                p["g2_audio_hardware_and_power_calls"],
                p["g2_common_data_transport_calls"],
                p["direct_cmsis_freertos_calls"],
            ),
            (80, 1, 8, 11, 1, 0),
        )
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
