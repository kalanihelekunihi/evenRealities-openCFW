#!/usr/bin/env python3
"""Guard conservative EM9305 residual-segment classification."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_em9305_residual_segments.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "analyze_em9305_residual_segments", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class Em9305ResidualSegmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_split_gap_trims_only_boundary_nops(self) -> None:
        body = b"\xe0\x78\x01\x02\xe0\x78\x03\x04\xe0\x78"
        parts = self.tool.split_gap(0x0030_3000, 0x0030_300A, body)
        self.assertEqual(
            [(item["size"], item["status"]) for item in parts],
            [
                (2, "stock_retained_alignment_nop"),
                (6, "stock_retained_unresolved_code_or_mixed"),
                (2, "stock_retained_alignment_nop"),
            ],
        )

    def test_expected_census_is_complete(self) -> None:
        self.assertEqual(sum(self.tool.EXPECTED_STATUS_BYTES.values()), 43_204)
        self.assertEqual(sum(self.tool.EXPECTED_SEGMENT_COUNTS.values()), 1_083)
        self.assertEqual(self.tool.EXPECTED_STATUS_BYTES["stock_retained_alignment_nop"], 1_812)
        self.assertEqual(self.tool.VECTOR_END - self.tool.VECTOR_START, 264)


if __name__ == "__main__":
    unittest.main()
