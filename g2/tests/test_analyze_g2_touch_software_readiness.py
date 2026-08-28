# SPDX-License-Identifier: MIT
"""Tests for the composed G2 touch software-readiness ledger."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_software_readiness.py"
S = importlib.util.spec_from_file_location("g2_touch_software_readiness", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchSoftwareReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.functions = {row["entry"]: row for row in cls.result["function_rows"]}

    def test_all_reachable_functions_have_one_disposition(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["function_count"], 63)
        self.assertEqual(metrics["function_status_counts"], {
            "external_eula_clean_room_required": 20,
            "project_fail_closed_contract": 8,
            "project_source_candidate": 10,
            "still_unclassified": 3,
            "unsupported_intentional_noop": 1,
            "upstream_apache_provider": 14,
            "upstream_runtime_provider": 7,
        })
        self.assertEqual(len(self.functions), 63)
        self.assertTrue(all(row["status"] for row in self.functions.values()))
        self.assertEqual(
            {entry for entry, row in self.functions.items()
             if row["status"] == "still_unclassified"},
            {0x465C, 0x465E, 0x4674},
        )

    def test_physical_code_accounting_deduplicates_shared_tails(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["mapped_code_physical_bytes"], 6316)
        self.assertEqual(metrics["code_unmapped_or_data_bytes"], 24048)
        self.assertEqual(6316 + 24048, 0x775C - 0x00C0)
        self.assertEqual(metrics["mapped_code_status_bytes"], {
            "external_eula_clean_room_required": 1948,
            "project_fail_closed_contract": 1560,
            "project_source_candidate": 816,
            "still_unclassified": 142,
            "unsupported_intentional_noop": 8,
            "upstream_apache_provider": 1068,
            "upstream_runtime_provider": 774,
        })
        self.assertEqual(sum(metrics["mapped_code_status_bytes"].values()), 6316)

    def test_whole_blob_byte_ledger_is_exhaustive(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["whole_blob_bytes"], 34464)
        self.assertEqual(metrics["payload_bytes"], 34432)
        self.assertEqual(sum(row["bytes"] for row in self.result["byte_rows"]),
                         metrics["whole_blob_bytes"])
        self.assertEqual(metrics["whole_blob_bucket_bytes"], {
            "generated_transport_fill": 512,
            "project_source_candidate": 816,
            "still_unclassified": 24190,
            "typed_external_or_unsupported": 8946,
        })
        self.assertEqual(sum(metrics["whole_blob_bucket_bytes"].values()), 34464)
        self.assertEqual(Counter(row["scope"] for row in self.result["byte_rows"])
                         .most_common(1)[0][1], 1)

    def test_pinned_ledger_digests(self):
        metrics = self.result["metrics"]
        self.assertEqual(
            metrics["function_ledger_digest"],
            "2eaa614f6a0a1d0270e29764db3f8f4565ac7bd890dc6485c4e54f34fdbc99c7",
        )
        self.assertEqual(
            metrics["byte_ledger_digest"],
            "6daf63278f00904cbd791da8bee30edd5e515ff1b631461581b270f887d9b230",
        )
        for row in self.result["byte_rows"]:
            self.assertEqual(len(row["address_set_sha256"]), 64)
            self.assertEqual(len(row["content_sha256"]), 64)

    def test_source_candidates_retain_actual_licenses(self):
        audits = self.result["source_audits"]
        self.assertEqual(audits["policy_helpers"]["license"], "MIT")
        self.assertEqual(audits["policy_helpers"]["exports"], 8)
        self.assertEqual(audits["i2c"]["license"], "MIT OR GPL-3.0-only")
        self.assertEqual(audits["sensing"]["license"], "MIT OR GPL-3.0-only")
        self.assertIn("hardware validation deferred by project direction",
                      audits["i2c"]["status"])
        self.assertIn("hardware validation deferred by project direction",
                      audits["sensing"]["status"])

    def test_upstream_and_eula_provider_boundaries_are_explicit(self):
        providers = self.result["provider_boundaries"]
        self.assertEqual(providers["infineon_cat2_pdl"]["license"], "Apache-2.0")
        self.assertEqual(providers["infineon_capsense"]["license"],
                         "LicenseRef-Infineon-EULA")
        self.assertEqual(providers["infineon_emeeprom"]["license"],
                         "LicenseRef-Infineon-EULA")
        self.assertIn("do not copy stock bytes",
                      providers["toolchain_runtime"]["use"])

    def test_resident_region_is_zero_byte_external_abi(self):
        abi = self.result["resident_external_abi"]
        self.assertTrue(all(row["availability"] == "external_unavailable_abi"
                            for row in abi))
        self.assertTrue(all(row["address"] is None or row["address"] >= 0x8680
                            for row in abi))
        self.assertEqual({row["address"] for row in abi if row["address"]},
                         {0xAA5C, 0xB0C4, 0xB0E8, 0xB374, 0xB4FC, 0xB51C})
        dfu = [row for row in abi if "DFU implementation" in row["role"]]
        self.assertEqual(len(dfu), 1)
        self.assertIsNone(dfu[0]["address"])

    def test_release_gate_is_honestly_closed_and_software_only(self):
        gate = self.result["release_readiness"]
        self.assertFalse(gate["software_complete"])
        self.assertEqual(gate["blocking_unclassified_code_or_data_bytes"], 24048)
        self.assertEqual(gate["blocking_unclassified_reachable_functions"], 3)
        self.assertFalse(gate["resident_abi_available"])
        self.assertFalse(gate["production_routed"])
        self.assertFalse(gate["hardware_validated"])
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifest_writes_are_deterministic(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                first_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in first}
                second = M.write_manifests(M.analyze())
                second_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in second}
                self.assertEqual(first_hashes, second_hashes)
                self.assertEqual(set(first_hashes), {
                    "g2-touch-software-readiness-functions.tsv",
                    "g2-touch-software-readiness-bytes.tsv",
                    "g2-touch-software-readiness-external-abi.tsv",
                    "g2-touch-software-readiness-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
