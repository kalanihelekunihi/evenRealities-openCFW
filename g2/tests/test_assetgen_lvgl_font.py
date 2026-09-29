#!/usr/bin/env python3
"""End-to-end gate for assetgen_lvgl_font.py.

Exercises the real, pinned `lv_font_conv` npm tool against a system font and
compiles the result against the vendored LVGL font headers. Skips cleanly
(does not fail the suite) when npx/npm or network access to the npm registry
is unavailable, since this generator's external, network-fetched dependency
is a documented, deliberate limitation (see the tool's module docstring).
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/assetgen_lvgl_font.py"
LVGL_SRC = ROOT.parent / "third-party/upstream/lvgl/src"

CANDIDATE_FONTS = [
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]


def load_tool():
    spec = importlib.util.spec_from_file_location("assetgen_lvgl_font", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _pin_reachable(m) -> bool:
    try:
        m._require_npx()
        m._verify_pinned_integrity()
    except m.AssetGenError:
        return False
    return True


class AssetgenLvglFontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_tool()
        cls.tmp = tempfile.TemporaryDirectory(prefix="assetgen-lvgl-font-")
        cls.dir = Path(cls.tmp.name)
        cls.font = next((f for f in CANDIDATE_FONTS if f.is_file()), None)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_never_reads_stock_image(self):
        source_text = TOOL.read_text()
        self.assertNotIn("blobs/official", source_text)
        self.assertNotIn("ota_s200_firmware_ota", source_text)

    def test_symbol_must_match_output_stem(self):
        with self.assertRaises(self.m.AssetGenError):
            self.m.generate(Path("/dev/null"), self.dir / "wrong_name.c", "other_symbol", 12, ["0x20-0x7e"])

    def test_missing_font_fails_closed(self):
        with self.assertRaises(self.m.AssetGenError):
            self.m.generate(self.dir / "no-such-font.ttf", self.dir / "no_such_font.c", "no_such_font", 12, ["0x20-0x7e"])

    @unittest.skipUnless(shutil.which("npx"), "npx (Node.js) not available on this host")
    def test_end_to_end_generate_and_compile(self):
        m = self.m
        if self.font is None:
            self.skipTest("no candidate system font found")
        if not _pin_reachable(m):
            self.skipTest("lv_font_conv pin not reachable (offline or npm unavailable)")
        output = self.dir / "smoke_font.c"
        report = m.generate(self.font, output, "smoke_font", size_px=12, ranges=["0x20-0x7e"], bpp=4)
        self.assertTrue(output.is_file())
        text = output.read_text()
        self.assertIn("const lv_font_t smoke_font", text)
        self.assertIn("SPDX-License-Identifier: MIT", text)
        self.assertIn(str(self.font), text)

        result = subprocess.run(
            [
                "clang", "-c", "-DLV_CONF_SKIP=1", "-DLV_LVGL_H_INCLUDE_SIMPLE=1",
                "-I", str(LVGL_SRC.parent), "-I", str(LVGL_SRC),
                str(output), "-o", str(self.dir / "smoke_font.o"),
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
