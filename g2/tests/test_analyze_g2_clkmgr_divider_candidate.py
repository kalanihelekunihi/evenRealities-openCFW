#!/usr/bin/env python3
"""Fail-closed tests for the Apollo clock-manager divider admission."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_clkmgr_divider_candidate as analyzer  # noqa: E402


class ClockManagerDividerAdmissionTests(unittest.TestCase):
    def test_authenticated_mapping_and_candidate(self) -> None:
        report = analyzer.run_audit()
        self.assertEqual(report["stock"]["functions_per_image"], 2)
        self.assertEqual(report["stock"]["bootloader_bytes"], 52)
        self.assertEqual(report["stock"]["apollo_main_bytes"], 52)
        self.assertEqual(report["stock"]["cross_image_bytes"], 104)
        self.assertTrue(report["candidate"]["semantic_c"])
        self.assertEqual(report["candidate"]["raw_instruction_bytes"], 0)
        self.assertTrue(report["candidate"]["production_routed"])
        self.assertEqual(report["hardware_validation"],
                         "deferred by project direction")

    def test_checked_in_summary_matches_live_audit(self) -> None:
        self.assertEqual(json.loads(analyzer.SUMMARY.read_text()),
                         analyzer.run_audit())

    def test_source_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-clkmgr-pin-") as tmp:
            changed = Path(tmp) / "candidate.c"
            changed.write_bytes(analyzer.SOURCE.read_bytes() + b"\n")
            pins = dict(analyzer.PINS)
            pins[changed] = pins.pop(analyzer.SOURCE)
            with mock.patch.object(analyzer, "PINS", pins):
                with self.assertRaises(analyzer.AuditError):
                    analyzer.authenticate(changed)


if __name__ == "__main__":
    unittest.main()
