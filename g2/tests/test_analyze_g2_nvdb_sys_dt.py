import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/analyze_g2_nvdb_sys_dt.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_nvdb_sys_dt", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2NvdbSysDtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_authenticated_surface(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 13)
        self.assertEqual(surface["body_bytes"], 5084)
        self.assertEqual(surface["owned_noncode_bytes"], 476)
        self.assertEqual(surface["direct_bl_ingress_sites"], 37)
        self.assertEqual(surface["direct_provider_calls"], 299)
        self.assertEqual(surface["stored_entry_pointers"], 2)
        self.assertEqual(surface["false_overlap_bls"], 1)
        self.assertEqual(surface["strict_interior_ingress"], 0)
        self.assertEqual(surface["raw_interior_windows"], 48)
        self.assertEqual(surface["aligned_interior_windows"], 8)

    def test_record_and_psn_abi(self) -> None:
        self.assertEqual(self.report["record"]["bytes"], 172)
        self.assertEqual(self.report["record"]["initialized_crc16"], "0x1DC7")
        self.assertEqual(self.report["record"]["aging_offsets"], [48, 88, 128])
        self.assertEqual(self.report["psn"]["legacy_entries"], 40)
        self.assertEqual(self.report["psn"]["otp_slots"], 8)
        self.assertEqual(self.report["psn"]["otp_slot_bytes"], 16)

    def test_migration_is_fail_closed(self) -> None:
        behavior = self.report["behavior"]
        self.assertFalse(behavior["migration_imports_flashdb_record"])
        self.assertFalse(behavior["migration_resets_aging"])
        self.assertTrue(behavior["migration_marks_legacy_psn"])
        self.assertTrue(behavior["migration_prefers_latest_valid_otp_psn"])

    def test_candidate_is_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
