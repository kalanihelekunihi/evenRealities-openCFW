# SPDX-License-Identifier: MIT
"""Tests for Touch terminal wrapper admission batch 20."""

import importlib.util, json, sys, tempfile, unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_terminal_wrappers_admission.py"
S = importlib.util.spec_from_file_location("g2_touch_terminal_admission", P)
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class TouchTerminalAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = M.analyze()

    def test_exact_gap_and_boundaries(self):
        self.assertEqual({r["entry"] for r in self.result["rows"]},
                         {0x1368, 0x25F8, 0x2972, 0x297A})
        m = self.result["metrics"]
        self.assertEqual((m["input_concrete_gap"], m["concrete_source_or_implementation_gap_after"]), (47, 43))
        self.assertEqual((m["admitted_instruction_bytes"], m["residual_gap_instruction_bytes"]), (72, 4478))
        self.assertTrue(all(not r["eula_provider_body_admitted"] and
                            not r["resident_table_dependency"] and
                            not r["mmio_execution"] for r in self.result["rows"]))

    def test_mit_target_closure_and_current_summary(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw); paths = M.write_manifests(self.result)
                current = json.loads(next(p for p in paths if p.name ==
                    "g2-touch-terminal-wrappers-admission-summary.json").read_text())
                self.assertEqual(current["authoritative_batch"], 20)
                self.assertEqual(current["hardware_validation"], "blocked by unavailable physical evidence")
                self.assertNotIn("g2-touch-current-source-readiness-summary.json",
                                 {p.name for p in paths})
        finally: M.MANIFEST_DIR = old


if __name__ == "__main__": unittest.main()
