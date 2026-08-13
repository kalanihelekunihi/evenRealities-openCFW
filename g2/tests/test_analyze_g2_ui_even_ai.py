import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_ui_even_ai.py"
S = importlib.util.spec_from_file_location("g2_ui_even_ai", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2UiEvenAiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface(self):
        surface = self.report["surface"]
        self.assertEqual(
            (
                surface["linked_functions"], surface["ghidra_discovered_functions"],
                surface["restored_functions"], surface["path_anchored_functions"],
                surface["raw_path_referencing_functions"], surface["body_bytes"],
                surface["instruction_bytes"], surface["physical_bytes"],
                surface["outer_pool_bytes"], surface["inline_literal_bytes"],
            ),
            (43, 15, 28, 2, 16, 8004, 8000, 8424, 420, 4),
        )
        self.assertEqual(
            (
                surface["direct_body_calls"], surface["internal_direct_body_calls"],
                surface["external_direct_body_calls"], surface["indirect_body_calls"],
                surface["direct_bl_entry_sites"], surface["stored_entry_pointers"],
            ),
            (512, 99, 413, 0, 131, 1),
        )

    def test_provider_accounting(self):
        provider = self.report["provider_boundary"]
        self.assertEqual(
            (
                provider["lvgl_calls"], provider["easylogger_calls"],
                provider["iar_dlib_calls"], provider["cmsis_freertos_calls"],
                provider["first_party_calls"],
            ),
            (182, 105, 22, 1, 103),
        )
        self.assertEqual(provider["lvgl_commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(
            provider["cmsis_freertos_commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertFalse(provider["new_version_discriminator"])
        self.assertFalse(provider["private_generating_commit_recoverable"])

    def test_object_contains_no_third_party_definitions(self):
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
