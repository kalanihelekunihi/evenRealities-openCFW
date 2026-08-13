#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_apollo_origin_accounting.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))
PLAN = ROOT / "build/source/flash-plan.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_apollo_origin_accounting", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOriginAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_range_mark_and_clear_are_bounded(self):
        mask = bytearray(8)
        self.analyzer._mark(mask, 98, 105, 100)
        self.assertEqual(list(mask), [1, 1, 1, 1, 1, 0, 0, 0])
        self.assertEqual(self.analyzer._clear_and_count(mask, 102, 110, 100), 3)
        self.assertEqual(sum(mask), 2)

    @unittest.skipUnless(CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(), "authenticated corpus/current build unavailable")
    def test_authenticated_origin_accounting(self):
        report = self.analyzer.analyze(PLAN, REPORT, CORPUS)
        self.assertEqual(report["component_accounting"]["opaque_base_bytes"], 3424780)
        self.assertEqual(report["flash_plan_metadata_gap"]["controlled_bytes_mislabeled_official_blob"], 1592)
        self.assertEqual(sum(report["opaque_origin_lower_bounds"].values()), 3424780)
        self.assertEqual(sum(report["third_party_path_anchored_bytes_by_family"].values()), 130000)
        self.assertEqual(len(report["ghidra_envelopes"]["rejected_oversized"]), 8)


if __name__ == "__main__":
    unittest.main()
