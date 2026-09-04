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
    str(ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth"),
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
        self.assertEqual(report["component_accounting"]["opaque_base_bytes"], 3046598)
        self.assertEqual(report["flash_plan_metadata_gap"]["controlled_bytes_mislabeled_official_blob"], 34192)
        self.assertEqual(report["flash_plan_metadata_gap"]["conservative_retained_delta_bytes"], 0)
        self.assertEqual(sum(report["opaque_origin_lower_bounds"].values()), 3046598)
        self.assertEqual(sum(report["third_party_path_anchored_bytes_by_family"].values()), 86364)
        self.assertEqual(len(report["ghidra_envelopes"]["rejected_oversized"]), 8)
        self.assertEqual(report["release_readiness_partition"], {
            "candidate_source_not_routed": 0,
            "typed_retained_or_external": 3046598,
        })
        self.assertEqual(report["unanchored_frontier_partition"]
                         ["typed_retained_unanchored_without_candidate"], 591115)
        self.assertEqual(
            sum(report["unanchored_frontier_partition"][key] for key in
                ("candidate_source_not_routed",
                 "typed_retained_unanchored_without_candidate")),
            591115,
        )
        self.assertEqual(
            report["unanchored_frontier_partition"]
            ["stock_address_set_sha256"],
            "8d3f6bd4ec698feaf7ef9df0d43e4f53f6f4e506eb64b6ce458d4cc5722822f1",
        )
        self.assertEqual(
            report["unanchored_frontier_partition"]
            ["production_routed_stock_address_set_sha256"],
            "8d3f6bd4ec698feaf7ef9df0d43e4f53f6f4e506eb64b6ce458d4cc5722822f1",
        )
        self.assertEqual(
            report["unanchored_frontier_partition"]
            ["retained_endpoint_stock_address_set_sha256"],
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        self.assertEqual(report["overlapping_object_closure_evidence"]["bytes"],
                         885418)
        self.assertFalse(report["overlapping_object_closure_evidence"]
                         ["additive_to_disjoint_release_totals"])


if __name__ == "__main__":
    unittest.main()
