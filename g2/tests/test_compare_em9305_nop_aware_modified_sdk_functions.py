#!/usr/bin/env python3
"""Guard NOP-aware EM9305 modified-function comparison identities."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_em9305_nop_aware_modified_sdk_functions.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "compare_em9305_nop_aware_modified_sdk_functions", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class Em9305NopAwareModifiedComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_selected_identity_is_pinned(self) -> None:
        self.assertEqual(self.tool.EXPECTED_FUNCTION_COUNT, 29)
        self.assertEqual(self.tool.EXPECTED_FUNCTION_BYTES, 4496)
        self.assertEqual(self.tool.EXPECTED_COMPARED_BYTES, 3868)
        self.assertEqual(sum(self.tool.EXPECTED_MISMATCH_COUNTS.values()), 53)
        self.assertEqual(len(self.tool.PLACEMENT_REPORT_SHA256), 64)
        self.assertIn("modified_same_size", self.tool.SELECTED_STATUS)


if __name__ == "__main__":
    unittest.main()
