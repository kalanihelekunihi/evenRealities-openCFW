import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_service_db_api.py"
S = importlib.util.spec_from_file_location("g2_service_db_api", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2ServiceDbApiTests(unittest.TestCase):
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
                surface["physical_bytes"], surface["outer_pool_bytes"],
            ),
            (11, 9, 2, 5, 7, 908, 1040, 132),
        )
        self.assertEqual(
            (
                surface["direct_body_calls"], surface["internal_direct_body_calls"],
                surface["external_direct_body_calls"], surface["indirect_body_calls"],
                surface["direct_bl_entry_sites"], surface["stored_entry_pointers"],
            ),
            (60, 1, 59, 0, 23, 6),
        )

    def test_provider_accounting_and_provenance(self):
        provider = self.report["provider_boundary"]
        self.assertEqual(
            (
                provider["flashdb_calls"], provider["cmsis_freertos_calls"],
                provider["easylogger_calls"], provider["first_party_calls"],
            ),
            (2, 7, 45, 5),
        )
        self.assertEqual(provider["flashdb_version"], "2.1.1")
        self.assertEqual(provider["flashdb_commit"], "714d6159e7e6afb267a3953756abca445c350e61")
        self.assertEqual(
            provider["cmsis_freertos_commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertTrue(provider["unsafe_zero_on_failure_fal_seam"])
        self.assertFalse(provider["new_version_discriminator"])
        self.assertFalse(provider["private_generating_commit_recoverable"])

    def test_object_contains_no_third_party_definitions(self):
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
