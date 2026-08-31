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
        self.assertTrue(
            report["candidate"][
                "retained_endpoint_dispatch_sequence_authenticated"
            ]
        )
        self.assertTrue(
            report["candidate"][
                "retained_endpoint_relocations_authenticated"
            ]
        )
        self.assertFalse(
            report["candidate"]["endpoint_stock_entries_unpatched"]
        )
        self.assertTrue(
            report["candidate"]["endpoint_candidate_exact_stock_abi"]
        )
        self.assertTrue(report["candidate"]["production_routed"])
        self.assertEqual(
            report["candidate"]["production_routed_functions"], 3
        )
        self.assertEqual(
            report["candidate"]["production_routed_physical_bytes"], 6614
        )
        self.assertEqual(report["candidate"]["remaining_candidate_functions"], 0)
        self.assertEqual(
            report["candidate"]["remaining_candidate_physical_bytes"], 0
        )
        self.assertIsNone(report["candidate"]["software_blocker"])
        self.assertEqual(
            report["hardware_validation"],
            "blocked by unavailable physical evidence",
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

    def test_missing_endpoint_routing_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-nemavg-route-") as tmp:
            changed = Path(tmp) / "overlay.json"
            overlay = json.loads(analyzer.OVERLAY.read_text())
            overlay["patch_sites"] = [
                item for item in overlay["patch_sites"]
                if item.get("runtime_address") != 0x0051B8F0
            ]
            changed.write_text(json.dumps(overlay), encoding="utf-8")
            with mock.patch.object(analyzer, "OVERLAY", changed):
                with self.assertRaisesRegex(
                    analyzer.AuditError, "production NemaVG route set changed"
                ):
                    analyzer.run_audit()


if __name__ == "__main__":
    unittest.main()
