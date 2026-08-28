#!/usr/bin/env python3
"""Fail-closed tests for the NemaVG stroke-cap source admission."""

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
import analyze_g2_nemavg_stroke_caps_candidate as analyzer  # noqa: E402


class NemaVGStrokeCapsAdmissionTests(unittest.TestCase):
    def test_authenticated_mapping_and_candidate(self) -> None:
        report = analyzer.run_audit()
        self.assertEqual(report["stock"]["functions"], 3)
        self.assertEqual(report["stock"]["function_body_bytes"], 6598)
        self.assertEqual(report["stock"]["physical_bytes"], 6614)
        self.assertEqual(
            [row["symbol"] for row in report["stock"]["records"]],
            ["draw_start_cap", "draw_end_cap", "draw_caps"],
        )
        self.assertTrue(report["candidate"]["semantic_c"])
        self.assertEqual(report["candidate"]["raw_instruction_bytes"], 0)
        self.assertFalse(report["candidate"]["production_routed"])
        self.assertEqual(
            report["hardware_validation"],
            "deferred by project direction",
        )

    def test_checked_in_summary_matches_live_audit(self) -> None:
        expected = json.loads(analyzer.SUMMARY.read_text())
        self.assertEqual(expected, analyzer.run_audit())

    def test_source_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-nemavg-pin-") as tmp:
            changed = Path(tmp) / "candidate.c"
            changed.write_bytes(analyzer.SOURCE.read_bytes() + b"\n")
            pins = dict(analyzer.PINS)
            pins[changed] = pins.pop(analyzer.SOURCE)
            with mock.patch.object(analyzer, "PINS", pins):
                with self.assertRaises(analyzer.AuditError):
                    analyzer.authenticate(changed)


if __name__ == "__main__":
    unittest.main()
