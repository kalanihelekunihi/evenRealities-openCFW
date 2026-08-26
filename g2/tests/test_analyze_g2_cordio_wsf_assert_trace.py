#!/usr/bin/env python3
"""Guard the fail-closed G2 WSF assert/trace recovery report."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_wsf_assert_trace.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_wsf_assert_trace", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioWsfAssertTraceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_stock_functions_and_ingress_are_closed(self) -> None:
        functions = self.report["functions"]
        trace = functions["WsfTrace"]
        assertion = functions["WsfAssert"]
        self.assertEqual(
            (trace["start"], trace["end_exclusive"], trace["size"]),
            (0x0052A63C, 0x0052A672, 54),
        )
        self.assertEqual(
            (assertion["start"], assertion["end_exclusive"], assertion["size"]),
            (0x00569A44, 0x00569ADE, 154),
        )
        self.assertEqual(len(trace["direct_bl_callers"]), 126)
        self.assertEqual(assertion["direct_bl_callers"], [0x0052A660])
        self.assertEqual(self.report["stored_entry_or_interior_pointers"], 0)

    def test_config_and_lineage_are_qualified(self) -> None:
        config = self.report["abi_and_config"]
        self.assertEqual(config["trace_buffer_bytes"], 1024)
        self.assertEqual(config["trace_assert_line"], 137)
        self.assertEqual(config["assert_hook_global"], "0x2007456C")
        self.assertTrue(config["AM_DEBUG_PRINTF"])
        self.assertTrue(config["WSF_TRACE_ENABLED"])
        self.assertFalse(config["normal_WSF_ASSERT_macros_effective"])
        lineage = self.report["lineage"]
        self.assertFalse(lineage["packetcraft_exact_body_route"])
        self.assertFalse(lineage["proprietary_source_copied"])
        self.assertEqual(len(lineage["dead_stripped_source_apis"]), 3)
        self.assertTrue(lineage["trace_path"].endswith("wsf_trace.c"))

    def test_candidate_and_readiness_matrix_are_routed(self) -> None:
        self.assertEqual(
            (self.report["candidate"]["functions"], self.report["candidate"]["stock_bytes"]),
            (2, 208),
        )
        self.assertEqual(self.report["candidate"]["production"], "routed")
        self.assertEqual(
            (
                self.report["candidate"]["compiled_text_bytes"],
                self.report["candidate"]["alignment_bytes"],
                self.report["candidate"]["strict_relocations"],
                self.report["candidate"]["guarded_redirects"],
            ),
            (170, 0, 5, 2),
        )
        matrix = self.report["compiler_matrix"]
        self.assertEqual(
            (matrix["compiler_profiles"], matrix["comparison_rows"]),
            (13, 26),
        )
        self.assertEqual(
            (matrix["raw_matches"], matrix["strict_normalized_matches"]),
            (0, 0),
        )
        self.assertEqual(matrix["best_size_gaps"]["WsfTrace"], 18)
        self.assertEqual(
            matrix["best_size_gaps"]["WsfAssert_pristine_baseline"], 118
        )

    def test_candidate_is_present_in_production_inputs(self) -> None:
        needle = "runtime_cordio_wsf_assert_trace_candidate"
        self.assertIn(
            needle,
            (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text(),
        )

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout)
        self.assertEqual(parsed["functions"]["WsfTrace"]["size"], 54)
        self.assertEqual(parsed["compiler_matrix"]["comparison_rows"], 26)


if __name__ == "__main__":
    unittest.main()
