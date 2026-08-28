# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave1.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave1/typed_boundaries.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave1-graphics-command-community.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave1", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_parent_frontier_is_reconciled_without_double_counting(self) -> None:
        self.assertEqual(
            self.report["parent_no_evidence"], {"functions": 1873, "bytes": 290704}
        )
        self.assertEqual(
            self.report["reconciled_existing_boundaries"],
            {
                "cordio_ll_sea": {"functions": 300, "bytes": 52866},
                "freetype_base": {"functions": 81, "bytes": 6928},
                "liblc3_attributed": {"functions": 31, "bytes": 14434},
                "apollo510_mspi_triplet": {"functions": 3, "bytes": 6250},
            },
        )
        typed = self.report["typed_non_census_boundaries_observed"]
        self.assertEqual((typed["clusters"], typed["bytes"]), (4, 1118))
        self.assertEqual(typed["unclassified"], {"clusters": 0, "bytes": 0})

    def test_largest_remaining_cluster_is_closed_as_typed_external(self) -> None:
        self.assertEqual(
            self.report["selected_range"],
            {"start": "0x005202EC", "end_exclusive": "0x00522A20"},
        )
        self.assertEqual(self.report["before"], {"functions": 1458, "bytes": 210226})
        self.assertEqual(self.report["newly_typed"], {"functions": 10, "bytes": 9002})
        self.assertEqual(self.report["after"], {"functions": 1448, "bytes": 201224})
        self.assertEqual(self.report["largest_remaining_envelope_bytes"], 5244)

    def test_every_body_is_sha_pinned_and_provider_claims_fail_closed(self) -> None:
        rows = self.report["records"]
        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(row["envelope_bytes"] for row in rows), 9002)
        self.assertEqual(len({row["entry"] for row in rows}), 10)
        self.assertEqual(
            {row["disposition"] for row in rows},
            {"typed-external-provider-unavailable"},
        )
        self.assertTrue(all(len(row["body_sha256"]) == 64 for row in rows))
        self.assertTrue(all(not row["source_identity_claimed"] for row in rows))
        self.assertTrue(all(not row["callable_implementation_available"] for row in rows))
        self.assertEqual(
            self.report["mapping_sha256"],
            "5ef61ced55ce6893c12a6b7c1a76501f05a6eeca0912eef4183261a300704536",
        )
        provider = self.report["provider"]
        self.assertEqual(provider["status"], "unavailable-and-unidentified")
        self.assertIsNone(provider["claimed_upstream_identity"])
        self.assertIsNone(provider["license"])

    def test_root_to_local_leaf_topology_is_complete(self) -> None:
        self.assertEqual(
            self.report["root_direct_calls"],
            {
                "0x0052262E": 2,
                "0x0052264E": 2,
                "0x005226B2": 2,
                "0x005226E8": 4,
                "0x005228B0": 1,
                "0x00522920": 4,
                "0x0052294C": 4,
                "0x00522956": 4,
                "0x00522A16": 3,
            },
        )
        root = self.report["records"][0]
        self.assertEqual((root["envelope_bytes"], root["corpus_body_bytes"]), (8374, 8300))

    def test_boundary_mutation_fails_closed(self) -> None:
        original = BOUNDARY.read_text()
        with tempfile.TemporaryDirectory() as temp:
            mutated = Path(temp) / "typed.tsv"
            mutated.write_text(original.replace("\t8374\t8300\t", "\t8372\t8300\t", 1))
            old = self.analyzer.BOUNDARY
            self.analyzer.BOUNDARY = mutated
            try:
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old

    def test_research_only_and_no_hardware_or_production_route(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (
            G2 / "Makefile",
            G2 / "tools/open_cfw.py",
            G2 / "tools/apollo_overlay.py",
        ):
            self.assertNotIn("apollo_opacity_wave1", path.read_text(errors="ignore"))
        self.assertIn("typed-external-provider-unavailable", DOC.read_text())

    def test_cli_is_deterministic(self) -> None:
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "opacity-wave1-typed-boundary-closed")


if __name__ == "__main__":
    unittest.main()
