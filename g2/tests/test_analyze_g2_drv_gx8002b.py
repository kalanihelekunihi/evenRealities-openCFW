import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_drv_gx8002b.py"
S = importlib.util.spec_from_file_location("g2_drv_gx8002b", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2DrvGx8002bTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface(self):
        surface = self.report["surface"]
        self.assertEqual(
            (
                surface["linked_functions"],
                surface["ghidra_discovered_functions"],
                surface["restored_functions"],
                surface["path_anchored_functions"],
                surface["raw_path_referencing_functions"],
                surface["body_bytes"],
                surface["physical_bytes"],
            ),
            (12, 9, 3, 3, 5, 1028, 1172),
        )
        self.assertEqual(surface["indirect_body_calls"], 0)

    def test_provider_accounting(self):
        provider = self.report["provider_boundary"]
        self.assertEqual(
            (
                provider["cmsis_core_linked_definitions"],
                provider["ambiqsuite_i2s_calls"],
                provider["cmsis_freertos_calls"],
                provider["easylogger_calls"],
                provider["first_party_calls"],
            ),
            (3, 13, 4, 45, 12),
        )
        self.assertEqual(
            provider["ambiqsuite_public_commit"],
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        )
        self.assertEqual(
            provider["ambiqsuite_source_sha256"],
            "16888e7bc9e2daf3ed936463c4e0ecfec73ea3c74c3c49b1fe60618b8aa86dc4",
        )
        self.assertFalse(provider["new_version_discriminator"])
        self.assertFalse(provider["private_generating_commit_recoverable"])

    def test_nationalchip_is_external_hardware_not_linked_sdk(self):
        identity = self.report["identity"]
        self.assertFalse(identity["nationalchip_lvp_code_linked"])
        self.assertEqual(
            identity["embedded_third_party_definitions"],
            ["__NVIC_EnableIRQ", "__NVIC_DisableIRQ", "__NVIC_SetPriority"],
        )

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
