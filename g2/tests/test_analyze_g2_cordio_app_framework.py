#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_app_framework.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    str(ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth"),
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_app_framework", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioApplicationFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_selected_source_boundary(self) -> None:
        snapshot = self.analyzer._verify_snapshot()
        self.assertEqual(snapshot["selected_commit"], self.analyzer.SELECTED_COMMIT)
        self.assertIsNone(snapshot["historical_g2_generating_commit"])

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_authenticated_lineage_and_legacy_objects(self) -> None:
        report = self.analyzer.analyze(CORPUS)
        self.assertEqual(report["stock_path_anchors"]["retained_paths"], 9)
        self.assertEqual(report["stock_path_anchors"]["anchored_functions"], 50)
        self.assertEqual(report["stock_path_anchors"]["anchored_body_bytes"], 29110)
        legacy = report["legacy_master_slave_objects"]["aggregate"]
        self.assertEqual(legacy["linked_functions"], 14)
        self.assertEqual(legacy["additional_recovered_functions"], 11)
        self.assertEqual(legacy["stored_callbacks"], 2)
        self.assertFalse(report["lineage"]["exact_source_text_identity"])
        production = report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["status"], "software_closed_hardware_deferred")
        self.assertTrue(production["legacy_master_slave_routed"])
        self.assertEqual(production["routed_functions"], 61)
        self.assertEqual(production["routed_anchored_functions"], 50)
        self.assertEqual(production["routed_anchored_body_bytes"], 29110)
        self.assertEqual(production["routed_stock_bytes"], 29870)
        self.assertEqual(production["legacy_ownership_bytes"], 948)
        self.assertEqual(production["legacy_relocations"], 29)
        self.assertEqual(production["application_runtime_ownership_bytes"], 4460)
        self.assertEqual(production["application_runtime_relocations"], 108)
        self.assertTrue(production["preexisting_app_database_routed"])
        self.assertEqual(production["remaining_anchored_functions"], 0)
        self.assertEqual(production["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertIn("required for future qualification", production["hardware_blocker"])

    def test_snapshot_hardware_policy_fails_closed(self) -> None:
        verifier = self.analyzer._load(
            "ambiqsuite_cordio_app_snapshot_policy_test",
            self.analyzer.SNAPSHOT_VERIFIER,
        )
        provenance = {
            "g2_boundary": dict(verifier.EXPECTED_HARDWARE_POLICY),
        }
        verifier._verify_hardware_policy(provenance)
        provenance["g2_boundary"]["hardware_validation"] = "blocked"
        with self.assertRaises(AssertionError):
            verifier._verify_hardware_policy(provenance)


if __name__ == "__main__":
    unittest.main()
