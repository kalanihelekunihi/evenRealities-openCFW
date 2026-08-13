#!/usr/bin/env python3
"""Guard the expanded EM9305 SDK archive census invariants."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_em9305_sdk_discovery.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("analyze_em9305_sdk_discovery", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305ExpandedSdkDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_manifest_and_report_identities_are_complete(self) -> None:
        manifest = self.tool.parse_manifest(self.tool.DEFAULT_MANIFEST)
        self.assertEqual(set(manifest), set(self.tool.EXPECTED_REPORT_SHA256))
        self.assertEqual(len(manifest), 16)
        self.assertTrue(all(len(item["git_blob"]) == 40 for item in manifest.values()))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest.values()))
        self.assertEqual(sum(self.tool.EXPECTED_RECORD_COUNTS.values()), 2180)

    def test_coverage_constants_are_exact_and_nonoverlapping(self) -> None:
        self.assertEqual(self.tool.EXPECTED_DISTINCT_FUNCTIONS, 1146)
        self.assertEqual(self.tool.EXPECTED_FUNCTION_BYTES, 132610)
        self.assertEqual(
            self.tool.EXPECTED_FUNCTION_BYTES + self.tool.KNOWN_ENFORCED_BYTES,
            139782,
        )
        self.assertLess(139782, self.tool.APP_SIZE)

    def test_round2_evidence_and_incremental_coverage_are_pinned(self) -> None:
        manifest = self.tool.parse_manifest(self.tool.DEFAULT_ROUND2_MANIFEST)
        self.assertEqual(set(manifest), set(self.tool.EXPECTED_ROUND2_REPORT_SHA256))
        self.assertEqual(len(manifest), 32)
        self.assertEqual(sum(self.tool.EXPECTED_ROUND2_RECORD_COUNTS.values()), 8542)
        self.assertEqual(self.tool.EXPECTED_ROUND2_DISTINCT_FUNCTIONS, 1201)
        self.assertEqual(self.tool.EXPECTED_ROUND2_FUNCTION_BYTES, 144740)
        self.assertEqual(self.tool.EXPECTED_ROUND2_NEW_FUNCTIONS, 67)
        self.assertEqual(self.tool.EXPECTED_ROUND2_NEW_BYTES, 13078)
        self.assertEqual(self.tool.EXPECTED_ALL_FUNCTIONS, 1311)
        self.assertEqual(self.tool.EXPECTED_ALL_BYTES, 152860)
        self.assertEqual(self.tool.APP_SIZE - self.tool.EXPECTED_ALL_BYTES, 58028)

    def test_low_floor_promotions_require_boundary_or_xref_evidence(self) -> None:
        self.assertEqual(self.tool.EXPECTED_ROUND1_MIN8_RECORDS, 2441)
        self.assertEqual(self.tool.EXPECTED_ROUND2_MIN8_RECORDS, 9607)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_CANDIDATES, 129)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_CANDIDATE_BYTES, 2196)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_PROMOTED, 124)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_PROMOTED_BYTES, 2106)
        self.assertEqual(len(self.tool.EXPECTED_LOW_FLOOR_REJECTED), 5)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_ALL_FUNCTIONS, 1435)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_ALL_BYTES, 154966)
        self.assertEqual(self.tool.EXPECTED_LOW_FLOOR_ALL_INTERVALS, 867)
        self.assertEqual(self.tool.APP_SIZE - self.tool.EXPECTED_LOW_FLOOR_ALL_BYTES, 55922)

    def test_function_identity_deduplicates_and_rejects_conflicts(self) -> None:
        functions = {}
        self.assertTrue(self.tool.add_function(
            functions,
            address=self.tool.APP_BASE,
            size=16,
            normalized_sha256="a" * 64,
            name="one",
            archive="first",
        ))
        self.assertFalse(self.tool.add_function(
            functions,
            address=self.tool.APP_BASE,
            size=16,
            normalized_sha256="a" * 64,
            name="alias",
            archive="second",
        ))
        self.assertEqual(functions[self.tool.APP_BASE]["names"], {"one", "alias"})
        with self.assertRaises(self.tool.AuditError):
            self.tool.add_function(
                functions,
                address=self.tool.APP_BASE,
                size=18,
                normalized_sha256="b" * 64,
                name="conflict",
                archive="third",
            )

    def test_interval_merger_preserves_gaps_and_coalesces_touching_spans(self) -> None:
        self.assertEqual(
            self.tool.merge_intervals(((8, 10), (0, 4), (4, 6), (9, 12))),
            [(0, 6), (8, 12)],
        )

    def test_critical_samples_are_inside_application(self) -> None:
        for address, name in self.tool.EXPECTED_CRITICAL_NAMES.items():
            self.assertTrue(name)
            self.assertGreaterEqual(address, self.tool.APP_BASE)
            self.assertLess(address, self.tool.APP_BASE + self.tool.APP_SIZE)

    def test_stock_image_identity_is_pinned(self) -> None:
        self.assertEqual(
            self.tool.sha256_file(self.tool.DEFAULT_IMAGE), self.tool.IMAGE_SHA256
        )


if __name__ == "__main__":
    unittest.main()
