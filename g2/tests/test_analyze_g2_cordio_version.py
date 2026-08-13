#!/usr/bin/env python3
"""Regression guards for the fail-closed Cordio version audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_cordio_version.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_version", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioVersionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer.MAIN.read_bytes()
        cls.report = cls.analyzer.analyze_bytes(cls.data)

    def test_image_identity_and_fail_closed_conclusion(self) -> None:
        self.assertEqual(self.report["image"]["sha256"], self.analyzer.MAIN_SHA256)
        self.assertEqual(self.report["status"], "whole-stack exact version unresolved")
        self.assertIsNone(self.report["exact_upstream_commit"])
        self.assertEqual(
            self.report["whole_stack_lower_bound"],
            "Packetcraft Cordio r20.05-or-later semantics",
        )
        self.assertEqual(
            self.report["bounded_equivalence_interval"]["releases"],
            ["r20.05", "r20.05a", "r20.05b", "r20.05c"],
        )

    def test_two_independent_release_discriminators_are_pinned(self) -> None:
        discriminators = self.report["discriminators"]
        self.assertEqual(
            discriminators["atts_csf_write_features"]["supports"],
            "r20.05-or-later behavior",
        )
        self.assertEqual(discriminators["dm_conn_sm_execute"]["events_per_state"], 8)
        self.assertEqual(discriminators["dm_conn_sm_execute"]["table_row_bytes"], 16)
        self.assertEqual(discriminators["dm_conn_sm_execute"]["action_sets"], 3)

    def test_wsf_configuration_and_vendor_port_boundary_are_pinned(self) -> None:
        wsf = self.report["discriminators"]["wsf_buffer_configuration"]
        self.assertEqual(wsf["free_marker"], "0xfaabd00d")
        self.assertEqual(wsf["trace_source_line"], 321)
        self.assertEqual(wsf["pool_descriptor_bytes"], 12)
        self.assertEqual(
            wsf["inferred_flags"],
            {
                "WSF_BUF_FREE_CHECK": True,
                "WSF_BUF_STATS": False,
                "WSF_BUF_STATS_HIST": False,
                "WSF_OS_DIAG": False,
            },
        )
        self.assertIn("FreeRTOS", wsf["source_port"])

    def test_source_paths_and_xrefs_are_not_path_only_evidence(self) -> None:
        paths = self.report["source_paths"]
        self.assertEqual(paths["dm_conn_sm"]["runtime_address"], 0x006DD114)
        self.assertEqual(paths["dm_conn_sm"]["pointer_xrefs_file_offsets"], [0xFC56C])
        self.assertEqual(paths["wsf_buf"]["runtime_address"], 0x006E20C4)
        self.assertEqual(paths["wsf_buf"]["pointer_xrefs_file_offsets"], [0xF8548])
        self.assertGreaterEqual(len(self.report["code_fingerprints"]), 7)

    def test_upstream_git_tree_blob_and_license_identities_are_complete(self) -> None:
        upstream = self.report["upstream"]
        self.assertEqual(upstream["license"], "Apache-2.0")
        self.assertEqual(len(upstream["license_git_blob"]), 40)
        self.assertEqual(len(upstream["license_sha256"]), 64)
        for release in upstream["releases"].values():
            self.assertEqual(len(release["commit"]), 40)
            self.assertEqual(len(release["tree"]), 40)
        for source in upstream["source_blobs"].values():
            self.assertEqual(len(source["git_blob"]), 40)
            self.assertEqual(len(source["sha256"]), 64)

    def test_ambiq_510_pin_does_not_overclaim_cordio_scope(self) -> None:
        ambiq = self.report["ambiqsuite_5_1_0_authenticated_local_scope"]
        self.assertEqual(ambiq["commit"], "5efc0228528a8adce5eae0d226fac85d2551eb3b")
        self.assertIn("no Cordio source", ambiq["scope"])

    def test_each_code_fingerprint_is_a_fail_closed_gate(self) -> None:
        for label, record in self.analyzer.CODE_SPANS.items():
            with self.subTest(label=label):
                mutated = bytearray(self.data)
                mutated[record["range"][0] - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaisesRegex(self.analyzer.AnalysisError, label):
                    self.analyzer.analyze_bytes(
                        bytes(mutated), enforce_image_identity=False
                    )

    def test_source_path_and_wsf_marker_drift_are_rejected(self) -> None:
        mutated_path = bytearray(self.data)
        mutated_path[self.analyzer.PATH_RECORDS["atts_csf"]["file_offset"]] ^= 1
        with self.assertRaisesRegex(self.analyzer.AnalysisError, "atts_csf"):
            self.analyzer.analyze_bytes(bytes(mutated_path), enforce_image_identity=False)

        mutated_magic = bytearray(self.data)
        mutated_magic[
            self.analyzer.WSF_FREE_MAGIC_ADDRESS - self.analyzer.LOAD_BASE
        ] ^= 1
        with self.assertRaisesRegex(self.analyzer.AnalysisError, "free marker"):
            self.analyzer.analyze_bytes(bytes(mutated_magic), enforce_image_identity=False)

    def test_cli_json_is_machine_readable(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "whole-stack exact version unresolved")
        self.assertIn("individual ABI", report["reuse_decision"])


if __name__ == "__main__":
    unittest.main()
