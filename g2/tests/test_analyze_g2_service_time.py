import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_time.py"
S = importlib.util.spec_from_file_location("g2_service_time", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface(self):
        surface = self.report["surface"]
        self.assertEqual(
            (
                surface["linked_functions"], surface["ghidra_discovered_functions"],
                surface["restored_functions"], surface["alternate_interior_entries"],
                surface["path_anchored_functions"], surface["body_bytes"],
                surface["physical_bytes"], surface["outer_pool_bytes"],
            ),
            (11, 10, 1, 1, 2, 1308, 1384, 76),
        )
        self.assertEqual(
            (
                surface["direct_body_calls"], surface["internal_direct_body_calls"],
                surface["external_direct_body_calls"], surface["indirect_body_calls"],
                surface["direct_bl_entry_sites"], surface["stored_entry_pointers"],
            ),
            (45, 11, 34, 0, 64, 6),
        )

    def test_calendar_contract(self):
        self.assertEqual(
            self.report["behavior"],
            {
                "unix_epoch_2000_seconds": 946684800,
                "seconds_per_day": 86400,
                "days_1970_to_2000": 10957,
                "timezone_unit_seconds": 900,
                "calendar_record_bytes": 40,
            },
        )

    def test_provider_accounting(self):
        provider = self.report["provider_boundary"]
        self.assertEqual(
            (
                provider["easylogger_calls"], provider["iar_dlib_calls"],
                provider["first_party_calls"], provider["direct_cmsis_freertos_calls"],
            ),
            (10, 8, 16, 0),
        )
        self.assertFalse(provider["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_route(self):
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertFalse(production["software_gap"])
        self.assertEqual(production["source_routed_functions"], 11)
        self.assertEqual(
            production["source_compiled_bytes"],
            {"apple-clang": 1658, "linux-clang": 1648},
        )
        self.assertEqual(production["strict_relocations"], 27)
        self.assertEqual(production["stock_body_bytes_displaced"], 1308)
        self.assertEqual(production["retained_diagnostic_pool_bytes"], 76)
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])


if __name__ == "__main__":
    unittest.main()
