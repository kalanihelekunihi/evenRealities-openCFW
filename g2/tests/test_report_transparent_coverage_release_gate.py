# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/report_transparent_coverage.py"
SPEC = importlib.util.spec_from_file_location("transparent_coverage_report", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TransparentCoverageReleaseGateTests(unittest.TestCase):
    def test_zero_opacity_alone_is_not_release_ready(self) -> None:
        summary = {
            "opaque_bytes": 0,
            "trapped_bytes": 128,
            "declared_data_bytes": 4096,
            "units_compiled": 90,
            "units_total": 100,
            "units_placed": 80,
        }
        blockers = MODULE.release_readiness_blockers(summary)
        self.assertEqual(len(blockers), 4)
        self.assertIn("128 trap bytes remain", blockers)
        self.assertIn("4096 vendor-derived declared-data bytes remain", blockers)
        self.assertIn("only 90 of 100 source units compile", blockers)
        self.assertIn("only 80 of 100 source units are placed", blockers)

    def test_opaque_bytes_are_reported_independently(self) -> None:
        summary = {
            "opaque_bytes": 7,
            "trapped_bytes": 0,
            "declared_data_bytes": 0,
            "units_compiled": 1,
            "units_total": 1,
            "units_placed": 1,
        }
        self.assertEqual(
            MODULE.release_readiness_blockers(summary),
            ["7 opaque bytes remain"],
        )

    def test_complete_open_source_image_has_no_blockers(self) -> None:
        summary = {
            "opaque_bytes": 0,
            "trapped_bytes": 0,
            "declared_data_bytes": 0,
            "units_compiled": 7370,
            "units_total": 7370,
            "units_placed": 7370,
        }
        self.assertEqual(MODULE.release_readiness_blockers(summary), [])


if __name__ == "__main__":
    unittest.main()
