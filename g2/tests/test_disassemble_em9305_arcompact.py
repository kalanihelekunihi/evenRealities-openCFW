#!/usr/bin/env python3
"""Guard the deterministic ARCv2 EM disassembly helper."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/disassemble_em9305_arcompact.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("disassemble_em9305_arcompact", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305ArcompactDisassemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_halfword_aligned_installed_range_is_accepted(self) -> None:
        self.assertEqual(self.tool.parse_range("0x311230:0x31125e"), (0x311230, 0x31125E))

    def test_unaligned_or_out_of_package_ranges_fail_closed(self) -> None:
        for value in ("0x311231:0x31125e", "0:2", "0x311230", "0x311230:0x311230"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                self.tool.parse_range(value)

    def test_stock_identity_constants_match_the_checked_in_blob(self) -> None:
        blob = self.tool.DEFAULT_IMAGE.read_bytes()
        self.assertEqual(len(blob), self.tool.IMAGE_SIZE)
        import hashlib

        self.assertEqual(hashlib.sha256(blob).hexdigest(), self.tool.IMAGE_SHA256)

    def test_prefixed_binutils_tool_is_resolved_inside_explicit_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "arc-linux-gnu-objdump"
            executable.touch()
            self.assertEqual(
                self.tool.resolve_tool("objdump", Path(directory)),
                executable,
            )


if __name__ == "__main__":
    unittest.main()
