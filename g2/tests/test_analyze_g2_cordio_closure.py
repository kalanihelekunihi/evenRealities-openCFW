#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_closure.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_closure", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def fixture(self):
        rows = []
        for name in self.analyzer.FOCUSED_PATH_AUDITS:
            boundary = "ambiq_port" if name.startswith("wsf_") or name == "hci_evt.c" else "public_packetcraft_candidate"
            rows.append({"relative": rf"third_party\cordio\fixture\{name}", "ownership_boundary": boundary})
        for name in self.analyzer.PRODUCT_APPLICATION_PATHS:
            rows.append({"relative": rf"third_party\cordio\ble-profiles\sources\apps\app\{name}", "ownership_boundary": "ambiq_or_product_application_layer"})
        return {"paths": rows}

    def test_closed_repository_inventory(self):
        report = self.analyzer.analyze_report(self.fixture())
        self.assertEqual(report["retained_path_census"]["focused_audit_present"], 27)
        self.assertEqual(report["retained_path_census"]["application_or_product_boundary"], 9)
        self.assertEqual(report["module_evidence_census"]["focused_module_analyzers"], 69)
        self.assertEqual(report["module_evidence_census"]["function_maps"], 69)
        self.assertEqual(report["module_evidence_census"]["provenance_manifests"], 70)
        self.assertTrue(report["ambiq_application_framework_source_admission"]["source_identification_closed"])
        self.assertFalse(report["ambiq_application_framework_source_admission"]["exact_source_text_identity"])
        self.assertEqual(report["copied_profile_source_admission"]["source_owned_functions"], 6)
        self.assertEqual(report["ambiq_profile_source_admission"]["source_derived_stock_functions"], 12)
        self.assertEqual(report["g2_profile_boundary_closure"]["modules"], 4)
        self.assertFalse(report["g2_profile_boundary_closure"]["third_party_source_dependency_identified"])
        self.assertEqual(report["amota_profile_lineage"]["ambiq_skeleton_derived_stock_functions"], 4)
        self.assertFalse(report["ring_profile_boundary"]["third_party_source_dependency_identified"])
        self.assertIsNone(report["historical_generating_commit"])

    def test_unknown_reusable_path_fails_closed(self):
        fixture = self.fixture()
        fixture["paths"][0]["relative"] = r"third_party\cordio\fixture\unknown.c"
        with self.assertRaisesRegex(self.analyzer.ClosureError, "retained reusable path set changed"):
            self.analyzer.analyze_report(fixture)

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_authenticated_aggregate_closure(self):
        report = self.analyzer.analyze(CORPUS)
        self.assertEqual(report["retained_path_census"]["unclassified_reusable_paths"], 0)
        self.assertEqual(report["retained_path_census"]["public_packetcraft_candidates"], 22)
        self.assertEqual(report["retained_path_census"]["ambiq_ports"], 5)


if __name__ == "__main__":
    unittest.main()
