#!/usr/bin/env python3
"""Tests for the authenticated Apollo Cordio source/function map."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_cordio_source_map.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_source_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioSourceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_call_constant_and_diagnostic_parsers(self) -> None:
        text = """void FUN_00530446(void) {
          FUN_0043d574(1,DAT_1,DAT_2,DAT_3,0x141,DAT_4,7);
          FUN_00530512(0x10000, 3);
        }"""
        self.assertEqual(self.analyzer._calls(text, 0x00530446), [0x0043D574, 0x00530512])
        self.assertEqual(self.analyzer._diagnostic_lines(text), [321])
        self.assertEqual(self.analyzer._literal_constants(text), [1, 3, 7, 321])

    def test_public_boundary_excludes_ports_and_app_layer(self) -> None:
        self.assertEqual(
            self.analyzer._boundary(r"third_party\cordio\wsf\sources\port\freertos\wsf_buf.c"),
            "ambiq_port",
        )
        self.assertEqual(
            self.analyzer._boundary(r"third_party\cordio\ble-profiles\sources\apps\app\app_main.c"),
            "ambiq_or_product_application_layer",
        )
        self.assertEqual(
            self.analyzer._boundary(r"third_party\cordio\ble-host\sources\stack\att\atts_csf.c"),
            "public_packetcraft_candidate",
        )

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_authenticated_closed_map(self) -> None:
        report = self.analyzer.analyze(CORPUS)
        self.assertEqual(report["census"]["retained_cordio_paths"], 36)
        self.assertEqual(report["census"]["paths_with_function_anchors"], 32)
        self.assertEqual(report["census"]["distinct_anchored_functions"], 114)
        self.assertIsNone(report["exact_upstream_commit"])
        self.assertEqual(
            report["authenticated_public_interval"]["releases"],
            ["r20.05", "r20.05a", "r20.05b", "r20.05c"],
        )


if __name__ == "__main__":
    unittest.main()
