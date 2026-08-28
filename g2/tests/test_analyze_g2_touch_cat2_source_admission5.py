# SPDX-License-Identifier: MIT
"""Tests for final exact CAT2 admission and the unavailable halt boundary."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_cat2_source_admission5.py"
S = importlib.util.spec_from_file_location("g2_touch_cat2_admission5", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchCat2Admission5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_final_nine_exact_apache_bodies(self):
        self.assertEqual(set(self.rows), {
            0x5CA0, 0x5CD0, 0x6044, 0x60C4, 0x6210,
            0x62B8, 0x6448, 0x64FC, 0x70B0,
        })
        self.assertEqual(self.rows[0x5CA0]["symbol"], "Cy_MSCLP_Capture")
        self.assertEqual(self.rows[0x5CD0]["symbol"], "Cy_MSCLP_Configure")
        self.assertEqual(self.rows[0x6044]["symbol"], "SlaveHandleHsMode")
        self.assertEqual(self.rows[0x60C4]["symbol"], "SlaveHandleStop")
        self.assertEqual(self.rows[0x6210]["symbol"], "SlaveHandleAck")
        self.assertEqual(self.rows[0x62B8]["symbol"], "SlaveHandleAddress")
        self.assertEqual(self.rows[0x6448]["symbol"], "SlaveHandleDataReceive")
        self.assertEqual(self.rows[0x64FC]["symbol"], "SlaveHandleDataTransmit")
        self.assertEqual(self.rows[0x70B0]["symbol"], "Cy_SysPm_RegisterCallback")

    def test_provider_identity_and_subsystem_counts(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["msclp_functions"], 2)
        self.assertEqual(metrics["scb_i2c_private_functions"], 6)
        self.assertEqual(metrics["syspm_functions"], 1)
        self.assertTrue(all(row["provider_commit"] == M.CAT2_COMMIT
                            for row in self.rows.values()))
        self.assertTrue(all(row["license"] == "Apache-2.0"
                            for row in self.rows.values()))
        self.assertEqual(metrics["row_digest"],
                         "6f50b021ebdaac1345b8cdcee3ee7ecb3e78ba8232f36d807d0a6d11b3aa898d")

    def test_halt_is_typed_but_not_source_admitted(self):
        self.assertNotIn(0x7038, self.rows)
        self.assertEqual(len(self.result["typed_unavailable"]), 1)
        halt = self.result["typed_unavailable"][0]
        self.assertEqual(halt["entry"], 0x7038)
        self.assertEqual(halt["status"],
                         "typed_external_system_provider_unavailable")
        self.assertIn("was removed", halt["evidence"])
        self.assertEqual(self.result["remaining"]["typed_unavailable_entry"],
                         "0x7038")

    def test_cumulative_gap_and_exclusions(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["cat2_gap_before"], metrics["cat2_gap_after"]),
                         (10, 1))
        self.assertEqual((metrics["semantic_gap_before"],
                          metrics["semantic_gap_after"]), (175, 166))
        self.assertEqual(metrics["unsafe_batch_admissions"], 0)
        self.assertIn("Em_EEPROM EULA", self.result["exclusions"])
        self.assertIn("fail-closed on host", self.result["integration"])
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifest_determinism(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                h1 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in first}
                second = M.write_manifests(M.analyze())
                h2 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in second}
                self.assertEqual(h1, h2)
                self.assertEqual(set(h1), {
                    "g2-touch-cat2-source-admission5.tsv",
                    "g2-touch-cat2-source-admission5-unavailable.tsv",
                    "g2-touch-cat2-source-admission5-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
