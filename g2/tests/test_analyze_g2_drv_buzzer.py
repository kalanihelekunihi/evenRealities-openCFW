import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_drv_buzzer.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_drv_buzzer", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2DrvBuzzerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 17,
            "body_bytes": 1520,
            "owned_noncode_bytes": 172,
            "physical_bytes": 1692,
            "direct_bl_entry_sites": 35,
            "exterior_bl_entry_sites": 18,
            "direct_body_calls": 88,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 11,
        })

    def test_audio_tables(self) -> None:
        audio = self.report["audio"]
        self.assertEqual(audio["peripheral_clock_hz"], 96_000_000)
        self.assertEqual(audio["frequency_divisor"], 1_000_000)
        self.assertEqual((audio["reload_entries"], audio["reload_bytes_per_entry"]),
                         (28, 2))
        self.assertEqual((audio["voice_records"], audio["voice_record_bytes"]),
                         (9, 50))
        self.assertEqual(audio["voice_triple_counts"],
                         [1, 14, 12, 1, 2, 1, 7, 7, 1])
        self.assertEqual(audio["duration_quantum_ms"], 62)
        self.assertEqual(audio["interval_quantum_ms"], 10)

    def test_runtime_contract(self) -> None:
        runtime = self.report["runtime"]
        self.assertEqual(runtime["timer_callback"], "0x005029fd")
        self.assertEqual(runtime["valid_voice_types"], 9)
        self.assertEqual((runtime["queued_play_event"], runtime["timer_event"]),
                         (1, 2))
        self.assertEqual(runtime["single_note_script"], "0x20074128")

    def test_remains_analysis_only(self) -> None:
        production = self.report["production"]
        self.assertIsNone(production["candidate"])
        self.assertFalse(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 0)
        self.assertFalse(production["source_inventory_available"])


if __name__ == "__main__":
    unittest.main()
