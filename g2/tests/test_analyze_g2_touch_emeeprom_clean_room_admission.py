#!/usr/bin/env python3
"""Fail-closed tests for clean-room Touch Em_EEPROM admission batch 25."""

import csv, importlib.util, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "tools/analyze_g2_touch_emeeprom_clean_room_admission.py"
S = importlib.util.spec_from_file_location("touch_eeprom_batch25_test", P); M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class TouchEmEepromAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = M.analyze()

    def test_exact_progress(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["admitted_functions"], metrics["admitted_instruction_bytes"]), (11, 1636))
        self.assertEqual((metrics["concrete_source_or_implementation_gap_after"], metrics["residual_gap_instruction_bytes"]), (8, 942))
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 8)

    def test_clean_room_boundary(self):
        for row in self.result["rows"]:
            self.assertTrue(row["backend_injected"]); self.assertFalse(row["eula_source_copied"])
            self.assertFalse(row["fixed_address_access"]); self.assertFalse(row["mmio_execution"])
        self.assertIn("migration", self.result["compatibility"])

    def test_target_compile_and_hardware_policy(self):
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(self.result["hardware_validation"], "deferred by project direction")
        self.assertEqual(self.result["hardware_blocker"], "deferred by project direction")
        self.assertNotIn("hardware_operations", self.result)

    def test_batch_writer_cannot_overwrite_final_current_summary(self):
        source = P.read_text(encoding="utf-8")
        self.assertNotIn('current.write_text', source)

    def test_manifests_match(self):
        with (M.MANIFEST_DIR / "g2-touch-emeeprom-clean-room-admission.tsv").open(newline="") as h:
            rows = list(csv.DictReader((line for line in h if not line.startswith("#")), delimiter="\t"))
        self.assertEqual({int(r["entry"], 0) for r in rows}, set(M.ADMISSIONS))
        summary = json.loads((M.MANIFEST_DIR / "g2-touch-emeeprom-clean-room-admission-summary.json").read_text())
        self.assertEqual(summary["metrics"], self.result["metrics"])


if __name__ == "__main__": unittest.main()
