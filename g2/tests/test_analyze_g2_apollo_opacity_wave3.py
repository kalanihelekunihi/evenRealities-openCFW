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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave3.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave3/typed_boundaries.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave3-vector-path-call-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave3", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave2_and_existing_aligned_memcpy_are_reconciled(self) -> None:
        self.assertEqual(
            self.report["wave2_residual"], {"functions": 1440, "bytes": 193152}
        )
        self.assertEqual(
            self.report["reconciled_since_wave2"],
            {"iar_aligned_memcpy": {"functions": 1, "official_opaque_bytes": 0}},
        )
        self.assertEqual(self.report["before"], {"functions": 1439, "bytes": 193152})

    def test_full_unresolved_call_closure_is_accounted(self) -> None:
        self.assertEqual(
            self.report["selected_root_range"],
            {"start": "0x00517E18", "end_exclusive": "0x00519280"},
        )
        self.assertEqual(self.report["newly_typed"], {"functions": 15, "bytes": 7672})
        self.assertEqual(
            self.report["closure_depths"],
            {
                "0": {"functions": 1, "bytes": 5224},
                "1": {"functions": 7, "bytes": 1498},
                "2": {"functions": 2, "bytes": 124},
                "3": {"functions": 1, "bytes": 684},
                "4": {"functions": 3, "bytes": 110},
                "5": {"functions": 1, "bytes": 32},
            },
        )
        self.assertEqual(self.report["after"], {"functions": 1424, "bytes": 185480})
        self.assertEqual(
            self.report["largest_remaining"],
            {"entry": "0x0043A698", "envelope_bytes": 5076},
        )

    def test_every_body_is_sha_pinned_and_fail_closed(self) -> None:
        rows = self.report["records"]
        self.assertEqual(len(rows), 15)
        self.assertEqual(sum(row["envelope_bytes"] for row in rows), 7672)
        self.assertEqual(len({row["entry"] for row in rows}), 15)
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
            "a2c2be89678710c965a165c2431a29f2c45ddeb5e3a541772f3607078b40cc90",
        )
        shortfalls = {
            row["entry"]: row["envelope_bytes"] - row["corpus_body_bytes"]
            for row in rows
            if row["envelope_bytes"] != row["corpus_body_bytes"]
        }
        self.assertEqual(shortfalls, {"0x00517E18": 54})

    def test_terminal_frontier_is_exhaustively_partitioned(self) -> None:
        self.assertEqual(
            self.report["terminal_partition"],
            {
                "prior_wave1_typed": ["0x005226B2"],
                "prior_wave2_typed": [
                    "0x00514AEC", "0x0051565C", "0x00516B34",
                    "0x0052266E", "0x005639E8",
                ],
                "existing_iar_source_recreated": ["0x004397A8", "0x00439C04"],
                "parent_classified_lvgl": ["0x004B127C"],
                "parent_zero_opaque_heap": [
                    "0x00484180", "0x004841D8", "0x0048429E",
                ],
            },
        )

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

    def test_boundary_mutation_fails_closed(self) -> None:
        original = BOUNDARY.read_text()
        with tempfile.TemporaryDirectory() as temp:
            mutated = Path(temp) / "typed.tsv"
            mutated.write_text(original.replace("\t5224\t5170\t", "\t5222\t5170\t", 1))
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
            self.assertNotIn("apollo_opacity_wave3", path.read_text(errors="ignore"))
        document = DOC.read_text()
        self.assertIn("typed-external-provider-unavailable", document)
        self.assertIn("Production routing remains prohibited", document)

    def test_cli_is_deterministic(self) -> None:
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(
            json.loads(first)["status"], "opacity-wave3-full-call-closure-typed"
        )


if __name__ == "__main__":
    unittest.main()
