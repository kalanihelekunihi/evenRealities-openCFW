# SPDX-License-Identifier: MIT
"""Tests for typed G2 touch-prefix helper/provider evidence."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_prefix_helper_evidence.py"
S = importlib.util.spec_from_file_location("g2_touch_prefix_helper_evidence", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchPrefixHelperEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_all_reachable_opaque_helpers_are_typed(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["helper_count"], 44)
        self.assertEqual(metrics["remaining_untyped_helpers"], 0)
        self.assertEqual(metrics["boundary_counts"], {
            "open_cfw_clean_room": 8,
            "infineon_cat2_pdl": 10,
            "infineon_capsense": 3,
            "infineon_emeeprom": 16,
            "toolchain_runtime": 7,
        })
        self.assertEqual(metrics["high_confidence_helpers"], 35)
        self.assertEqual(metrics["medium_confidence_helpers"], 9)
        self.assertEqual(metrics["evidence_digest"],
                         "27b3373ad1475a6370eb0acb338f4564e10ba523a4e35d10ab6f61406b00329d")
        self.assertEqual(set(self.rows), set(M.HELPERS))

    def test_exact_runtime_abi_names(self):
        expected = {
            0x73C0: "__aeabi_uidiv",
            0x74CC: "__aeabi_uidivmod",
            0x74D4: "__aeabi_idiv",
            0x76A0: "__aeabi_idivmod",
            0x76A8: "__aeabi_idiv0",
            0x76D4: "memset",
            0x772C: "memcpy",
        }
        for entry, name in expected.items():
            row = self.rows[entry]
            self.assertEqual(row["proposed_name"], name)
            self.assertEqual(row["boundary"], "toolchain_runtime")
            self.assertTrue(row["name_status"].startswith("exact_"))

    def test_cat2_pdl_matches_and_register_evidence(self):
        expected = {
            0x1180: "Cy_SysLib_DelayCycles",
            0x65F4: "Cy_SCB_I2C_Init",
            0x6F14: "NVIC_SetPriority",
            0x6F74: "Cy_SysInt_SetVector",
            0x6FA8: "Cy_SysInt_Init",
            0x6FF0: "Cy_SysLib_Delay",
        }
        for entry, name in expected.items():
            self.assertEqual(self.rows[entry]["proposed_name"], name)
            self.assertEqual(self.rows[entry]["boundary"], "infineon_cat2_pdl")
        self.assertEqual(self.rows[0x6F14]["mmio_literals"],
                         [0xE000E100, 0xE000ED00])
        provider = self.result["providers"]["infineon_cat2_pdl"]
        self.assertEqual(provider["commit"],
                         "35f1714623cfea682d5e285af80d50416b4c7bbc")
        self.assertEqual(provider["license"], "Apache-2.0")

    def test_emeeprom_crc_and_status_family(self):
        self.assertEqual(self.rows[0x4B68]["proposed_name"], "CalcChecksum")
        self.assertIn("0xFF", self.rows[0x4B68]["evidence"])
        self.assertIn("0x31", self.rows[0x4B68]["evidence"])
        self.assertEqual(self.rows[0x57AC]["proposed_name"], "Cy_Em_EEPROM_Read")
        statuses = {value for row in self.rows.values()
                    if row["boundary"] == "infineon_emeeprom"
                    for value in row["status_literals"]}
        self.assertTrue({0x093E0000, 0x093E0001, 0x093E0002,
                         0x093E0003, 0x093E0004} <= statuses)
        provider = self.result["providers"]["infineon_emeeprom"]
        self.assertEqual(provider["license"], "LicenseRef-Infineon-EULA")
        self.assertIn("clean-room", provider["use"])

    def test_capsense_is_typed_not_promoted_to_exact_symbols(self):
        for entry in (0x4A04, 0x4A36, 0x4A6C):
            row = self.rows[entry]
            self.assertEqual(row["boundary"], "infineon_capsense")
            self.assertEqual(row["name_status"], "typed_provider_candidate")
        provider = self.result["providers"]["infineon_capsense"]
        self.assertEqual(provider["commit"],
                         "b68b744eb75fe976fc5ddd7b16e04e1a5a54bdd3")
        self.assertEqual(provider["license"], "LicenseRef-Infineon-EULA")

    def test_mit_boundary_and_no_hardware_claim(self):
        self.assertIn("no hardware", self.result["analysis_mode"])
        self.assertEqual(self.result["providers"]["open_cfw_clean_room"]["license"],
                         "MIT")
        self.assertEqual(self.result["remaining_opacity"]["untyped_helpers"], 0)
        self.assertEqual(self.result["remaining_opacity"]["historical_source_commit_proven"], 0)
        self.assertTrue(any("do not copy" in rule
                            for rule in self.result["clean_room_rules"]))

    def test_toolchain_license_is_not_guessed(self):
        provider = self.result["providers"]["toolchain_runtime"]
        self.assertEqual(provider["license"],
                         "LicenseRef-Upstream-Toolchain-Runtime")
        self.assertIn("upstream", provider["use"])

    def test_manifest_writes_are_deterministic(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                one = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in first}
                second = M.write_manifests(M.analyze())
                two = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in second}
                self.assertEqual(one, two)
                self.assertEqual(set(one), {
                    "g2-touch-prefix-helper-evidence.tsv",
                    "g2-touch-prefix-provider-boundaries.tsv",
                    "g2-touch-prefix-helper-evidence-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
