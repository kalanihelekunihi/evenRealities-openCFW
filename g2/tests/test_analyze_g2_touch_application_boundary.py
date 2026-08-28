# SPDX-License-Identifier: MIT
"""Tests for touch application/startup admission and clean-room contracts."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_application_boundary.py"
S = importlib.util.spec_from_file_location("g2_touch_application_boundary", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchApplicationBoundaryAnalyzerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.exact = {row["entry"]: row for row in cls.result["exact_rows"]}
        cls.contracts = {row["entry"]: row for row in cls.result["contract_rows"]}

    def test_exact_critical_helpers_are_apache_admitted(self):
        self.assertEqual(set(self.exact), {0x1192, 0x119A})
        self.assertEqual(self.exact[0x1192]["symbol"],
                         "Cy_SysLib_EnterCriticalSection")
        self.assertEqual(self.exact[0x119A]["symbol"],
                         "Cy_SysLib_ExitCriticalSection")
        self.assertTrue(all(row["license"] == "Apache-2.0"
                            for row in self.exact.values()))
        self.assertEqual(self.result["upstream"]["commit"], M.CAT2_COMMIT)
        self.assertEqual(self.result["upstream"]["source_file_sha256"],
                         M.SYSLIB_ASSEMBLY_SHA256)

    def test_all_other_application_rows_are_non_source_contracts(self):
        metrics = self.result["metrics"]
        self.assertEqual(len(self.contracts), 97)
        self.assertEqual(metrics["platform_startup_contracts"], 46)
        self.assertEqual(metrics["touch_application_contracts"], 51)
        self.assertTrue(all(row["status"] ==
                            "typed_clean_room_reimplementation_contract"
                            for row in self.contracts.values()))
        self.assertTrue(all(not row["concrete_source"] and not row["implemented"]
                            for row in self.contracts.values()))

    def test_accounting_does_not_overstate_completeness(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["application_ambiguity_before"],
                          metrics["application_ambiguity_after"]), (99, 0))
        self.assertEqual((metrics["actionable_semantic_source_before"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (111, 109))
        self.assertEqual(metrics["concrete_implemented_contracts"], 0)
        self.assertEqual(self.result["remaining"]["clean_room_contracts_unimplemented"], 97)
        self.assertIn("not implementations", self.result["remaining"]["note"])

    def test_topology_and_isolation(self):
        self.assertEqual(self.result["metrics"]["component_sizes"],
                         [71, 5, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(self.result["metrics"]["external_dependency_entries"], 61)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertIn("EULA bodies remain external", self.result["exclusions"])
        self.assertGreater(self.result["adapters"]["critical"]["target_object_bytes"], 0)
        self.assertGreater(
            self.result["adapters"]["application_contract"]["target_object_bytes"], 0)

    def test_manifest_determinism(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                h1 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in first}
                second = M.write_manifests(M.analyze())
                h2 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in second}
                self.assertEqual(h1, h2)
                self.assertEqual(set(h1), {
                    "g2-touch-application-upstream-admission.tsv",
                    "g2-touch-application-clean-room-contracts.tsv",
                    "g2-touch-application-topology.tsv",
                    "g2-touch-application-boundary-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
