import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_production_mic.py"
S = importlib.util.spec_from_file_location("g2_production_mic", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ProductionMicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface_and_restored_stereo_callback(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["raw_path_references"], s["raw_path_referencing_functions"],
                s["body_bytes"], s["physical_bytes"],
                s["outer_pool_and_alignment_bytes"], s["reachable_instructions"],
            ),
            (6, 5, 1, 5, 7, 6, 898, 1000, 102, 359),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (64, 0, 64, 0, 8, 2),
        )

    def test_pcm_callback_and_capture_modes(self):
        b = self.report["behavior"]
        self.assertEqual((b["listener_id"], b["codec_capture_mode"], b["pdm_capture_mode"]), (0x10B, 0, 1))
        self.assertEqual(b["channel_scratch_bytes"], 400)
        self.assertTrue(b["stereo_callback_only_accepts_source_zero"])
        self.assertTrue(b["stereo_extracted_channels_concatenated"])
        self.assertEqual(b["single_callback_accepts_sources"], [0, 1])
        self.assertTrue(b["raw_pcm_forwarded_when_extraction_disabled"])

    def test_no_hidden_dsp_dependency(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (p["easylogger_and_compact_calls"], p["iar_dlib_memory_calls"], p["g2_codec_pdm_pcm_calls"], p["direct_cmsis_freertos_calls"]),
            (35, 5, 24, 0),
        )
        self.assertFalse(self.report["identity"]["nationalchip_lvp_code_linked"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
