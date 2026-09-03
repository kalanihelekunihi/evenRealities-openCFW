#!/usr/bin/env python3
"""Fail-closed tests for the Apollo clock-manager divider admission."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_clkmgr_divider_candidate as analyzer  # noqa: E402


class ClockManagerDividerAdmissionTests(unittest.TestCase):
    def test_linux_boot_report_uses_the_canonical_admission_provider(self) -> None:
        self.assertEqual(
            analyzer.BOOT_LINUX_REPORT,
            ROOT
            / "build/canonical-provider/linux-clang/apollo_bootloader/build-report.json",
        )
        self.assertNotIn(
            "build-linux-clock-record",
            analyzer.BOOT_LINUX_REPORT.as_posix(),
        )

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
                         "blocked by unavailable physical evidence")
        self.assertEqual(
            (
                report["production"]["package"]["size"],
                report["production"]["package"]["sha256"],
            ),
            (
                4_750_780,
                "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27",
            ),
        )
        self.assertEqual(
            (
                report["production"]["linux_clang"]["package"]["size"],
                report["production"]["linux_clang"]["package"]["sha256"],
            ),
            (
                4_750_764,
                "617c37fc25913f5590a15a410e3f35687c50328e2ef1618b0a67fbbd8f9ef559",
            ),
        )

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

    def test_stale_package_identity_in_summary_fails_closed(self) -> None:
        stored = json.loads(analyzer.SUMMARY.read_text(encoding="utf-8"))
        stale = copy.deepcopy(stored)
        stale["production"]["package"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-clkmgr-summary-"
        ) as temporary:
            receipt = Path(temporary) / "summary.json"
            receipt.write_text(
                json.dumps(stale, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(analyzer.AuditError, "summary is stale"):
                analyzer.require_summary_current(stored, receipt)
            receipt.write_text(
                json.dumps(stored, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            analyzer.require_summary_current(stored, receipt)

    def test_make_target_regenerates_summary_before_tests(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        recipe = makefile.split("clkmgr-divider-candidate:", 1)[1].split(
            "\n\n", 1
        )[0]
        self.assertIn(
            "tools/analyze_g2_clkmgr_divider_candidate.py --write-manifest",
            recipe,
        )


if __name__ == "__main__":
    unittest.main()
