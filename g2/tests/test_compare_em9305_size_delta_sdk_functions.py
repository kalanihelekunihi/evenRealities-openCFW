#!/usr/bin/env python3
"""Guard EM9305 size-delta opcode comparison helpers."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_em9305_size_delta_sdk_functions.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "compare_em9305_size_delta_sdk_functions", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class Em9305SizeDeltaComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_opcode_sequence_comparison(self) -> None:
        result = self.tool.opcode_comparison(
            ["enter_s", "ld_s", "add_s", "leave_s"],
            ["enter_s", "ld_s", "sub_s", "add_s", "leave_s"],
        )
        self.assertEqual(result["matching_instruction_count"], 4)
        self.assertEqual(result["stock_only_instruction_count"], 1)
        self.assertGreater(result["sequence_ratio"], 0.8)

    def test_objdump_tabs_disambiguate_hexadecimal_arc_mnemonic(self) -> None:
        rows = self.tool.parse_instructions(
            "  304204:\t2554 1f00           \tadd1\tr0,r13,0x3c\n"
            "  304208:\t202f 0000           \tjl_s\t[blink]\n"
        )
        self.assertEqual(
            rows,
            [
                (0x304204, "add1", "r0,r13,0x3c"),
                (0x304208, "jl_s", "[blink]"),
            ],
        )

    def test_selected_totals_are_pinned(self) -> None:
        self.assertEqual(self.tool.EXPECTED_FUNCTION_COUNT, 13)
        self.assertEqual(self.tool.EXPECTED_STOCK_BYTES, 3940)
        self.assertEqual(self.tool.EXPECTED_ARCHIVE_BYTES, 3820)
        self.assertEqual(len(self.tool.EXPECTED_SEQUENCE_METRICS), 13)
        self.assertEqual(self.tool.EXPECTED_ARCHIVE_INSTRUCTIONS, 1256)
        self.assertEqual(self.tool.EXPECTED_STOCK_INSTRUCTIONS, 1298)
        self.assertEqual(self.tool.EXPECTED_MATCHING_INSTRUCTIONS, 1225)
        self.assertEqual(len(self.tool.PLACEMENT_REPORT_SHA256), 64)


if __name__ == "__main__":
    unittest.main()
