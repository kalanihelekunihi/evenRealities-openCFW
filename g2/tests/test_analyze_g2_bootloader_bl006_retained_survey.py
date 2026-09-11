#!/usr/bin/env python3
"""Tests for the BL-006 apollo_bootloader retained-byte reachability survey."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_bootloader_bl006_retained_survey.py"
SPEC = importlib.util.spec_from_file_location(
    "analyze_g2_bootloader_bl006_retained_survey", PATH
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Bl006RetainedSurveyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.survey()

    def test_catalog_matches_the_bl006_work_item(self) -> None:
        # These totals are the exact figures named by the BL-006 work item;
        # a change here means the catalog no longer matches the item and
        # must be regenerated from flash-plan.json, not hand-edited.
        self.assertEqual(self.report["region_count"], 77)
        self.assertEqual(self.report["total_bytes"], 5892)
        self.assertEqual(self.report["work_item"], "BL-006")

    def test_authenticated_bytes_are_unchanged(self) -> None:
        # survey() already raises SurveyError on any pin mismatch; reaching
        # this point means every one of the 77 regions still hashes to the
        # value recorded when the catalog was built from the flash plan.
        self.assertEqual(len(self.report["regions"]), 77)

    def test_no_region_shows_a_surviving_external_branch(self) -> None:
        # As of this survey, every inbound branch found anywhere in the
        # stock disassembly that lands in one of the 77 regions originates
        # either from a stock span the build already overwrites, or from
        # another one of the 77 still-retained regions itself (which is not
        # evidence of a live reference). None originates from genuinely
        # separate, still-executing code. If a future change to overlay.json
        # or the stock blob makes that no longer true, this test must go red
        # and the flagged region must be investigated before BL-006 assumes
        # it is dead.
        flagged = [
            region for region in self.report["regions"]
            if region["verdict"] == "POSSIBLY_REACHABLE_NEEDS_REVIEW"
        ]
        self.assertEqual(flagged, [])
        self.assertEqual(self.report["needs_review_count"], 0)

    def test_verdict_counts_are_corroborated(self) -> None:
        by_verdict: dict[str, int] = {}
        for region in self.report["regions"]:
            by_verdict[region["verdict"]] = by_verdict.get(region["verdict"], 0) + 1
        self.assertEqual(
            by_verdict,
            {
                "corroborated_unreachable_control_flow": 30,
                "no_control_flow_reference_found": 47,
            },
        )

    def test_no_region_start_address_appears_as_a_data_literal_elsewhere(self) -> None:
        # A cheap, over-approximate signal only: none of the 77 region start
        # addresses occurs as a raw little-endian 32-bit word anywhere in the
        # stock image, so none of them is an obvious pointer-table target.
        # A nonzero count here would not by itself prove reachability, but it
        # would be a concrete lead worth investigating before closing that
        # region.
        for region in self.report["regions"]:
            self.assertEqual(
                region["literal_word_match_count"],
                0,
                f"{region['start']} appears as a literal word elsewhere; "
                "investigate before treating it as safely retained data",
            )


if __name__ == "__main__":
    unittest.main()
