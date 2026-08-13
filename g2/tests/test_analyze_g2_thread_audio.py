import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_thread_audio.py"
S = importlib.util.spec_from_file_location("g2_thread_audio", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ThreadAudioTests(unittest.TestCase):
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
                s["body_bytes"], s["physical_bytes"], s["outer_pool_bytes"],
                s["inline_alignment_bytes"],
            ),
            (31, 12, 19, 3, 24, 13, 2954, 3258, 302, 2),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (203, 20, 183, 1, 43, 3),
        )

    def test_behavior_contract(self):
        self.assertEqual(
            self.report["behavior"],
            {
                "message_queue_capacity": 50,
                "message_bytes": 12,
                "known_dispatch_ids": 8,
                "watchdog_period_ticks": 2000,
                "codec_activity_threshold": 20,
                "dma_interrupt_max_age_ticks": 40,
            },
        )

    def test_provider_accounting_and_commits(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_calls"], p["cmsis_freertos_calls"],
                p["cmsis_wrapper_count"], p["iar_dlib_calls"],
                p["closed_codec_gx8002b_calls"], p["other_first_party_calls"],
                p["bounded_first_party_indirect_calls"],
            ),
            (120, 20, 14, 1, 19, 23, 1),
        )
        self.assertEqual(p["cmsis_freertos_commit"], "d213f261b5be6bb29a7cce8b84071706b72f4d53")
        self.assertEqual(p["freertos_kernel_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
        self.assertEqual(p["cmsis_5_commit"], "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c")
        self.assertFalse(p["nationalchip_lvp_code_linked"])
        self.assertFalse(p["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
