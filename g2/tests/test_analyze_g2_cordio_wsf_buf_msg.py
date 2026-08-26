#!/usr/bin/env python3
"""Guard the fail-closed G2 WSF buffer/message recovery report."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_wsf_buf_msg.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_wsf_buf_msg", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioWsfBufferMessageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_stock_modules_and_ingress_are_closed(self) -> None:
        modules = self.report["modules"]
        self.assertEqual(
            (modules["wsf_buf"]["start"], modules["wsf_buf"]["end_exclusive"], modules["wsf_buf"]["size"]),
            (0x00530364, 0x00530512, 430),
        )
        self.assertEqual(
            (modules["wsf_msg"]["start"], modules["wsf_msg"]["end_exclusive"], modules["wsf_msg"]["size"]),
            (0x004BF990, 0x004BFA0E, 126),
        )
        self.assertEqual(
            (len(modules["wsf_buf"]["functions"]), len(modules["wsf_msg"]["functions"])),
            (3, 7),
        )
        by_name = {
            row["name"]: row
            for unit in ("wsf_buf", "wsf_msg")
            for row in modules[unit]["functions"]
        }
        self.assertEqual(by_name["WsfBufInit"]["direct_bl_callers"], [0x004B7F7C])
        self.assertEqual(len(by_name["WsfBufAlloc"]["direct_bl_callers"]), 24)
        self.assertEqual(len(by_name["WsfBufFree"]["direct_bl_callers"]), 28)
        self.assertEqual(len(by_name["WsfMsgAlloc"]["direct_bl_callers"]), 69)
        self.assertEqual(by_name["WsfMsgPeek"]["direct_bl_callers"], [0x0052A800, 0x0052AE82])
        self.assertEqual(modules["stored_entry_or_interior_pointers"], 0)

    def test_initialized_pool_configuration_is_exact(self) -> None:
        pools = self.report["pool_configuration"]
        self.assertEqual(
            pools["descriptors"],
            [[16, 8], [32, 4], [64, 10], [480, 20]],
        )
        self.assertEqual(
            (pools["memory_address"], pools["capacity"], pools["used"], pools["spare"]),
            ("0x2004FA98", 0x2940, 0x2930, 0x10),
        )
        self.assertEqual(self.report["buffer_abi"]["internal_pool_size"], 12)
        self.assertEqual(self.report["message_abi"]["payload_offset"], 8)

    def test_lineage_candidate_and_readiness_qualifications(self) -> None:
        self.assertIn("proprietary oracle only", self.report["lineage"]["buffer"])
        self.assertIn("Apache-2.0", self.report["lineage"]["message"])
        self.assertEqual(len(self.report["lineage"]["unbounded_buffer_source_apis"]), 4)
        self.assertEqual(
            (self.report["candidate"]["behaviorally_recreated_functions"], self.report["candidate"]["behaviorally_recreated_bytes"]),
            (10, 556),
        )
        self.assertFalse(self.report["candidate"]["proprietary_source_copied"])
        matrix = self.report["compiler_matrix"]
        self.assertEqual((matrix["variants"], matrix["compiler_profiles"], matrix["comparison_rows"]), (2, 13, 78))
        self.assertEqual(matrix["best_aggregate_lane"], "stock_warn_seam__O3")
        self.assertEqual(matrix["best_function_gaps"]["WsfBufFree"], 2)
        self.assertEqual((matrix["raw_matches"], matrix["strict_normalized_matches"]), (0, 0))

    def test_candidates_are_guarded_routed_in_production(self) -> None:
        self.assertEqual(self.report["candidate"]["production"], "routed")
        metrics = self.report["candidate"]["production_metrics"]
        self.assertEqual(
            (
                metrics["buffer"]["compiled_text_bytes"],
                metrics["buffer"]["strict_relocations"],
                metrics["buffer"]["guarded_redirects"],
            ),
            (582, 5, 3),
        )
        self.assertEqual(
            (
                metrics["message"]["compiled_text_bytes"],
                metrics["message"]["alignment_bytes"],
                metrics["message"]["strict_relocations"],
                metrics["message"]["guarded_redirects"],
            ),
            (114, 12, 8, 7),
        )
        overlay = (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
        self.assertIn("runtime_cordio_wsf_buf_candidate.c", overlay)
        self.assertIn("runtime_cordio_wsf_msg_candidate.c", overlay)

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout)
        self.assertEqual(parsed["pool_configuration"]["used"], 0x2930)
        self.assertEqual(
            parsed["modules"]["wsf_msg"]["functions"][-1]["name"],
            "WsfMsgPeek",
        )


if __name__ == "__main__":
    unittest.main()
