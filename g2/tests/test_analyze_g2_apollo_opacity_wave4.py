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
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave4.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave4/typed_boundaries.tsv"
ZERO_BOUNDARY = G2 / "research/admission/apollo_opacity_wave4/reconciled_zero_opaque.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave4-orientation-calibration-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave4", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave3_and_zero_opaque_rows_are_reconciled(self) -> None:
        self.assertEqual(
            self.report["wave3_residual"], {"functions": 1424, "bytes": 185480}
        )
        self.assertEqual(
            self.report["reconciled_zero_opaque"], {"functions": 8, "bytes": 0}
        )
        self.assertEqual(self.report["before"], {"functions": 1416, "bytes": 185480})

    def test_complete_graph_and_provider_continuation_are_accounted(self) -> None:
        self.assertEqual(
            self.report["selected_root_range"],
            {"start": "0x0043A698", "end_exclusive": "0x0043BA6C"},
        )
        self.assertEqual(self.report["newly_typed"], {"functions": 20, "bytes": 8116})
        self.assertEqual(
            self.report["closure_depths"],
            {
                "0": {"typed_functions": 1, "typed_bytes": 5076, "zero_opaque_rows": 0},
                "1": {"typed_functions": 13, "typed_bytes": 2806, "zero_opaque_rows": 7},
                "2": {"typed_functions": 4, "typed_bytes": 96, "zero_opaque_rows": 1},
                "3": {"typed_functions": 2, "typed_bytes": 138, "zero_opaque_rows": 0},
            },
        )
        self.assertEqual(self.report["after"], {"functions": 1396, "bytes": 177364})
        self.assertEqual(
            self.report["largest_remaining"],
            {"entry": "0x00519290", "envelope_bytes": 5056},
        )
        self.assertEqual(
            self.report["terminal_partition"], {"existing_iar_sqrtf": ["0x004397A8"]}
        )

    def test_typed_bodies_are_sha_pinned_and_dispositions_are_precise(self) -> None:
        rows = self.report["records"]
        self.assertEqual(len(rows), 20)
        self.assertEqual(sum(row["envelope_bytes"] for row in rows), 8116)
        self.assertEqual(len({row["entry"] for row in rows}), 20)
        self.assertEqual(
            sum(row["disposition"] == "typed-external-provider-unavailable" for row in rows),
            18,
        )
        iar = [row for row in rows if row["provider_identity"] == "IAR-DLIB-memset-family"]
        self.assertEqual([row["entry"] for row in iar], ["0x0043C0E4", "0x0043C0EC"])
        self.assertTrue(
            all(row["disposition"] == "typed-external-iar-dlib-source-unavailable" for row in iar)
        )
        self.assertTrue(all(row["license_status"] == "proprietary-source-unavailable" for row in iar))
        self.assertTrue(all(not row["callable_implementation_available"] for row in rows))
        self.assertEqual(
            self.report["mapping_sha256"],
            "c051a78a2aa5f76167978893adcfa7d8699fd3cfe95e3db5400b7da9f5f75623",
        )
        shortfalls = {
            row["entry"]: row["envelope_bytes"] - row["corpus_body_bytes"]
            for row in rows if row["envelope_bytes"] != row["corpus_body_bytes"]
        }
        self.assertEqual(shortfalls, {"0x0043A698": 124, "0x0043BA98": 1250})

    def test_zero_opaque_does_not_imply_source_ownership(self) -> None:
        rows = self.report["zero_opaque_records"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["official_opaque_bytes"] == 0 for row in rows))
        reconciliations = [row["reconciliation"] for row in rows]
        self.assertEqual(reconciliations.count("existing-source-recreated-IAR-memcpy"), 1)
        self.assertEqual(
            reconciliations.count("zero-opaque-interior-accounted-by-0x0043BA98-envelope"),
            7,
        )

    def test_positive_ingress_context_stays_distinct_from_algorithm_identity(self) -> None:
        provider = self.report["provider"]
        self.assertIn("sole caller 0x0055F848", provider["ingress"])
        self.assertEqual(provider["npmx_relation"], "explicitly not part of Nordic nPMX")
        self.assertIsNone(provider["algorithm_identity"])
        self.assertIsNone(provider["algorithm_license"])
        self.assertEqual(
            provider["iar_exception"],
            {
                "span": "0x0043C0E4-0x0043C14A",
                "identity": "IAR DLIB memset family",
                "license_status": "proprietary-source-unavailable",
            },
        )

    def test_typed_and_zero_table_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            typed = temp_path / "typed.tsv"
            typed.write_text(BOUNDARY.read_text().replace("\t5076\t4952\t", "\t5074\t4952\t", 1))
            zero = temp_path / "zero.tsv"
            zero.write_text(ZERO_BOUNDARY.read_text().replace("\t166\t0\t104\t", "\t164\t0\t104\t", 1))
            old_typed, old_zero = self.analyzer.BOUNDARY, self.analyzer.ZERO_BOUNDARY
            try:
                self.analyzer.BOUNDARY = typed
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_typed
                self.analyzer.ZERO_BOUNDARY = zero
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY, self.analyzer.ZERO_BOUNDARY = old_typed, old_zero

    def test_research_only_and_no_hardware_or_production_route(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave4", path.read_text(errors="ignore"))
        document = DOC.read_text()
        self.assertIn("typed-external-provider-unavailable", document)
        self.assertIn("Production admission", document)

    def test_cli_is_deterministic(self) -> None:
        command = [sys.executable, str(ANALYZER)]
        first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(
            json.loads(first)["status"],
            "opacity-wave4-orientation-calibration-closure-typed",
        )


if __name__ == "__main__":
    unittest.main()
