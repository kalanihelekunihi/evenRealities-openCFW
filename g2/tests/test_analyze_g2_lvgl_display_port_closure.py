#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_lvgl_display_port_closure.py"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_lvgl_display_port_closure", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LvglDisplayPortClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_authenticated_display_port_closure(self):
        paths = self.analyzer._load(self.analyzer.PATH_ANALYZER)
        report = self.analyzer.analyze(paths.DEFAULT_IMAGE, self.analyzer.DEFAULT_REPORT, CORPUS)
        self.assertEqual(report["display_port"]["source_owned_functions"], 7)
        self.assertEqual(report["display_port"]["stock_executable_bytes"], 638)
        self.assertEqual(report["input_boundary"]["third_party_ambiq_input_port_paths"], 0)
        self.assertIsNone(report["provenance"]["historical_generating_commit"])

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_missing_redirect_fails_closed(self):
        paths = self.analyzer._load(self.analyzer.PATH_ANALYZER)
        path_report = paths.analyze(image=paths.DEFAULT_IMAGE, corpus_root=CORPUS)
        build_report = json.loads(self.analyzer.DEFAULT_REPORT.read_text())
        build_report = copy.deepcopy(build_report)
        build_report["overlay"]["patched_sites"] = [
            row for row in build_report["overlay"]["patched_sites"]
            if row.get("target_function") != "open_cfw_lv_display_sync"
        ]
        with self.assertRaisesRegex(self.analyzer.ClosureError, "source replacement missing"):
            self.analyzer.analyze_report(
                path_report, build_report, paths.DEFAULT_IMAGE.read_bytes(), paths.LOAD_BASE
            )

    @unittest.skipUnless(CORPUS.is_dir(), "authenticated 64-shard corpus unavailable")
    def test_new_vendor_input_port_fails_closed(self):
        paths = self.analyzer._load(self.analyzer.PATH_ANALYZER)
        path_report = paths.analyze(image=paths.DEFAULT_IMAGE, corpus_root=CORPUS)
        path_report = copy.deepcopy(path_report)
        path_report["paths"].append({
            "relative": r"third_party\lvgl_v9.3\lvgl_ambiq_porting\lv_ambiq_input.c",
            "root": "third_party",
            "third_party_dependency": "lvgl_v9.3",
        })
        build_report = json.loads(self.analyzer.DEFAULT_REPORT.read_text())
        with self.assertRaisesRegex(self.analyzer.ClosureError, "port-path census changed"):
            self.analyzer.analyze_report(
                path_report, build_report, paths.DEFAULT_IMAGE.read_bytes(), paths.LOAD_BASE
            )


if __name__ == "__main__":
    unittest.main()
