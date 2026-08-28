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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave2.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave2/typed_boundaries.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave2-vector-path-community.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave2", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave1_and_existing_zero_byte_runtime_row_are_reconciled(self) -> None:
        self.assertEqual(
            self.report["wave1_residual"], {"functions": 1448, "bytes": 201224}
        )
        self.assertEqual(
            self.report["reconciled_since_wave1"],
            {"iar_sqrtf": {"functions": 1, "official_opaque_bytes": 0}},
        )
        self.assertEqual(self.report["before"], {"functions": 1447, "bytes": 201224})

    def test_largest_envelope_and_complete_direct_residual_close(self) -> None:
        self.assertEqual(
            self.report["selected_root_range"],
            {"start": "0x005156B8", "end_exclusive": "0x00516B34"},
        )
        self.assertEqual(
            self.report["community_address_hull"],
            {
                "start": "0x00514AEC",
                "end_exclusive": "0x00563F3C",
                "contiguous": False,
            },
        )
        self.assertEqual(self.report["newly_typed"], {"functions": 7, "bytes": 8072})
        self.assertEqual(self.report["after"], {"functions": 1440, "bytes": 193152})
        self.assertEqual(
            self.report["largest_remaining"],
            {"entry": "0x00517E18", "envelope_bytes": 5224},
        )

    def test_all_bodies_are_pinned_and_fail_closed(self) -> None:
        rows = self.report["records"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row["envelope_bytes"] for row in rows), 8072)
        self.assertEqual(len({row["entry"] for row in rows}), 7)
        self.assertEqual(
            {row["disposition"] for row in rows},
            {"typed-external-provider-unavailable"},
        )
        self.assertTrue(all(len(row["body_sha256"]) == 64 for row in rows))
        self.assertTrue(all(not row["source_identity_claimed"] for row in rows))
        self.assertTrue(all(row["license_claimed"] is None for row in rows))
        self.assertTrue(all(not row["callable_implementation_available"] for row in rows))
        self.assertEqual(
            self.report["mapping_sha256"],
            "7e2bfdeec9489a848c1f0da5c42c09ee52d53ace7651996869db46af2063dc66",
        )
        decoded_shortfalls = {
            row["entry"]: row["envelope_bytes"] - row["corpus_body_bytes"]
            for row in rows
            if row["envelope_bytes"] != row["corpus_body_bytes"]
        }
        self.assertEqual(decoded_shortfalls, {"0x005156B8": 66, "0x005639E8": 30})

    def test_provider_context_does_not_become_identity_or_license(self) -> None:
        provider = self.report["provider"]
        self.assertEqual(
            provider["status"], "candidate-family-known-exact-function-unresolved"
        )
        self.assertEqual(provider["resolved_stock_symbols_checked"], 11)
        self.assertEqual(provider["selected_symbols_resolved"], 0)
        self.assertIsNone(provider["claimed_upstream_function_identity"])
        self.assertIsNone(provider["license"])
        self.assertIn("original IAR archive", provider["reason"])

    def test_root_call_topology_is_exhaustively_partitioned(self) -> None:
        self.assertEqual(
            self.report["root_direct_calls"],
            {
                "0x004397A8": 3,
                "0x0050969C": 1,
                "0x00514AEC": 7,
                "0x0051565C": 3,
                "0x00516B34": 6,
                "0x005179D0": 6,
                "0x0052266E": 3,
                "0x005226B2": 6,
                "0x005639E8": 3,
            },
        )
        self.assertEqual(
            self.report["root_direct_partition"],
            {
                "newly_typed": [
                    "0x00514AEC",
                    "0x0051565C",
                    "0x00516B34",
                    "0x005179D0",
                    "0x0052266E",
                    "0x005639E8",
                ],
                "prior_wave1_typed": ["0x005226B2"],
                "existing_iar_source_recreated": ["0x004397A8"],
                "existing_parent_first_party": ["0x0050969C"],
            },
        )

    def test_boundary_mutation_fails_closed(self) -> None:
        original = BOUNDARY.read_text()
        with tempfile.TemporaryDirectory() as temp:
            mutated = Path(temp) / "typed.tsv"
            mutated.write_text(original.replace("\t5244\t5178\t", "\t5242\t5178\t", 1))
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
            self.assertNotIn("apollo_opacity_wave2", path.read_text(errors="ignore"))
        document = DOC.read_text()
        self.assertIn("typed-external-provider-unavailable", document)
        self.assertIn("Nothing here is routed into production", document)

    def test_cli_is_deterministic(self) -> None:
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "opacity-wave2-typed-boundary-closed")


if __name__ == "__main__":
    unittest.main()
