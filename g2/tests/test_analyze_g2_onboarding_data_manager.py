import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_onboarding_data_manager.py"
S = importlib.util.spec_from_file_location("g2_onboarding_data_manager", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2OnboardingDataManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_physical_object(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["body_bytes"], s["physical_bytes"],
                s["outer_pool_and_alignment_bytes"], s["reachable_instructions"],
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (7, 7, 0, 5, 826, 932, 106, 343, 52, 0, 52, 0, 11, 0),
        )
        self.assertEqual(s["raw_bl_like_compressed_data_decodes"], 1)
        self.assertEqual(s["strict_interior_code_ingress"], 0)

    def test_onboarding_state_and_protocol_contract(self):
        b = self.report["behavior"]
        self.assertEqual(b["process_record_address"], "0x200F4800")
        self.assertEqual(b["process_record_bytes"], 3)
        self.assertEqual(b["accepted_common_data_types"], [1, 2, 3])
        self.assertTrue(b["type_one_updates_process_under_mutex"])
        self.assertEqual((b["flag_save_event_bit"], b["peer_service_id"], b["peer_role"]), (4, 0x10, 5))
        self.assertEqual(b["peer_message_ids"], [0x09, 0x0D, 0x0E])
        self.assertEqual((b["phone_notification_command"], b["phone_notification_tag"]), (3, 5))

    def test_reusable_edges_are_admitted_or_bounded(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_calls"], p["cmsis_freertos_calls"], p["iar_memset_calls"],
                p["g2_ota_role_display_policy_calls"], p["g2_peer_transport_calls"],
                p["closed_onboarding_kvdb_calls"], p["closed_onboarding_protobuf_calls"],
            ),
            (35, 3, 3, 3, 3, 4, 1),
        )
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(p["new_version_discriminator"])
        self.assertFalse(p["private_generating_commit_recoverable"])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
