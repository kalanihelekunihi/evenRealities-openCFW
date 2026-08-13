#!/usr/bin/env python3
"""Guard the authenticated, production-excluded LVGL source mapping."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_lvgl_source_mapping.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_lvgl_source_mapping", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Apollo Ghidra corpus unavailable")
class LVGLSourceMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_mapping_closes_function_path_lines_and_behavior(self) -> None:
        item = self.report["mapping"]
        self.assertEqual(item["function"], "lv_iter_create")
        self.assertEqual((item["entry"], item["end_exclusive"], item["size"]), (0x005C3B00, 0x005C3BB2, 178))
        self.assertEqual(item["retained_path_run"], 0x006E8794)
        self.assertEqual(item["pointer_cell"], 0x005C3BC4)
        self.assertEqual(item["assertion_lines"], [65, 68, 79])
        self.assertEqual(item["direct_callers_in_decompiled_corpus"], [])
        self.assertIn("context_offset_8", item["behavioral_pins"])

    def test_report_refuses_translation_unit_or_production_claim(self) -> None:
        self.assertIn("production-excluded", self.report["analysis_mode"])
        limitations = " ".join(self.report["limitations"])
        self.assertIn("whole translation unit", limitations)
        self.assertIn("not a production source-replacement candidate", limitations)

    def test_source_mutation_fails_closed(self) -> None:
        raw = self.analyzer.SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "lv_iter.c"
            changed.write_bytes(raw.replace(b"LV_ASSERT_MALLOC(iter);", b"LV_ASSERT_NULL(iter);", 1))
            with self.assertRaises(self.analyzer.AuditError):
                self.analyzer.analyze(CORPUS, source=changed)

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--ghidra-corpus", str(CORPUS), "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout)
        self.assertEqual(parsed["mapping"]["source"], "src/misc/lv_iter.c")


if __name__ == "__main__":
    unittest.main()
