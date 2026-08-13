#!/usr/bin/env python3
"""Guard the fail-closed G2 ring-buffer lineage and boundary audit."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_ring_buffer.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_ring_buffer", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RingBufferAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_lineage_interval_and_selection_are_explicit(self) -> None:
        upstream = self.report["upstream"]
        self.assertEqual(upstream["compatible_floor_commit"], "cda00e1efb815bad5100757f0d10d117f633ced6")
        self.assertEqual(upstream["compatible_ceiling_commit"], "190e30bebcec22d7311fd941179d70b4f439c441")
        self.assertEqual(upstream["selected_commit"], upstream["compatible_ceiling_commit"])
        self.assertFalse(upstream["exact_vendor_checkout_proven"])

    def test_complete_cluster_and_abi_are_pinned(self) -> None:
        self.assertEqual(self.report["identity"]["stock_cluster"]["size"], 264)
        self.assertEqual(len(self.report["segments"]), 8)
        self.assertEqual(self.report["recovery"]["stock_executable_bytes"], 250)
        self.assertEqual(self.report["abi"]["object_size"], 16)
        self.assertEqual(self.report["abi"]["full_policy"], "overwrite oldest byte")

    def test_production_closure_is_fully_admitted(self) -> None:
        recovery = self.report["recovery"]
        self.assertEqual(recovery["production_integration_percent"], 100)
        self.assertEqual(recovery["production_source_bytes"], 248)
        self.assertEqual(recovery["production_generated_alignment_bytes"], 4)
        self.assertEqual(
            recovery["production_generated_entry_replacement_bytes"], 252
        )

    def test_source_and_external_callers_are_discriminating(self) -> None:
        self.assertIn("third_party\\ringBuffer\\ringbuffer.c", self.report["identity"]["source_path"])
        callers = self.report["callers"]
        self.assertEqual(callers["0x00598160"], ((0x0058FB62, "08f0fdfa"),))
        self.assertEqual(callers["0x005981C4"], ((0x0058FB24, "08f04efb"),))
        self.assertEqual(callers["0x0059820A"], ((0x0058FB32, "08f06afb"),))

    def test_cli_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"identification_percent": 100', result.stdout)


if __name__ == "__main__":
    unittest.main()
