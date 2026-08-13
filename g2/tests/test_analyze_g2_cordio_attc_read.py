#!/usr/bin/env python3
"""Guard the bounded G2 Cordio ATT client read-unit evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_read.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_read", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AttcReadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 4)
        self.assertEqual(module["source_inventory_functions"], 7)
        self.assertEqual(module["linked_function_bytes"], 414)
        self.assertEqual(module["physical_bytes"], 416)
        self.assertEqual(
            module["source_only_functions"],
            ["AttcReadLongReq", "AttcReadMultipleReq", "AttcReadByGroupTypeReq"],
        )
        self.assertEqual(module["direct_bl_ingress_sites"], 3)
        self.assertEqual(module["registered_function_pointers"], 2)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertTrue(report["architecture"]["bearer_aware_read_long"])
        self.assertTrue(report["lineage"]["independent_release_discriminator"])


if __name__ == "__main__":
    unittest.main()
