#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_goodix_v170_source_overlap.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("g2_goodix_v170_overlap", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GoodixV170SourceOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        if not cls.module.DEFAULT_SDK.is_dir():
            raise unittest.SkipTest("complete selected GR551x SDK 1.7.0 checkout unavailable")
        cls.report = cls.module.analyze()

    def test_complete_source_tree_is_swept(self) -> None:
        sdk = self.report["sdk"]
        self.assertEqual(sdk["c_header_paths"], 2167)
        self.assertEqual(sdk["unique_source_blobs"], 1681)
        self.assertEqual(sdk["multi_string_overlap_blobs"], 4)

    def test_only_app_error_adds_an_exact_source(self) -> None:
        classes = self.report["classifications"]
        self.assertEqual(
            classes["new_exact_goodix_source"],
            ["components/libraries/app_error/app_error.c"],
        )
        self.assertEqual(classes["new_dependency_families_beyond_goodix_app_error"], [])

    def test_cmbacktrace_overlap_is_not_misattributed(self) -> None:
        cross = self.report["cross_checks"]
        self.assertEqual(cross["cmbacktrace_stock_print_info_entries"], 39)
        self.assertFalse(cross["goodix_cortex_backtrace_exact_stock_source"])

    def test_bundled_nanopb_0_4_2_is_excluded(self) -> None:
        cross = self.report["cross_checks"]
        self.assertEqual(cross["sdk_nanopb_version"], "0.4.2")
        self.assertEqual(cross["stock_nanopb_pristine_lower_bound"], "0.4.7")
        self.assertTrue(cross["sdk_nanopb_0_4_2_excluded_by_stock_pb_read"])


if __name__ == "__main__":
    unittest.main()
