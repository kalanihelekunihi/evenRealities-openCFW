#!/usr/bin/env python3
"""Guard the bounded G2 Cordio ATT client write-unit evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_write.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_write", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AttcWriteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 2)
        self.assertEqual(module["source_inventory_functions"], 5)
        self.assertEqual(module["linked_function_bytes"], 124)
        self.assertEqual(module["physical_bytes"], 124)
        self.assertEqual(
            module["source_only_functions"],
            ["attcPrepWriteAllocMsg", "AttcPrepareWriteReq", "AttcExecuteWriteReq"],
        )
        self.assertEqual(module["direct_bl_ingress_sites"], 1)
        self.assertEqual(module["registered_function_pointers"], 1)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertFalse(report["lineage"]["independent_release_discriminator"])
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["stock_bytes_replaced"], 124)
        self.assertEqual(report["production"]["source_owned_bytes_added"], 144)
        self.assertEqual(report["production"]["alignment_bytes"], 2)
        self.assertEqual(report["production"]["strict_relocations"], 2)
        self.assertEqual(report["production"]["guarded_redirects"], 2)


if __name__ == "__main__":
    unittest.main()
