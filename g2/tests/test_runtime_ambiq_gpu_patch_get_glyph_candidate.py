#!/usr/bin/env python3
"""Qualify the production-excluded Ambiq GPU vector-glyph lookup candidate."""

from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_gpu_patch_get_glyph_candidate.c"
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_gpu_patch_get_glyph_candidate_host.c"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
FUNCTION = "open_cfw_ambiq_gpu_get_glyph_candidate"
PUBLIC_SECTION = (
    188,
    188,
    "73c9856b02da209dbe68f4985f79cee430c4bea04dfadd66cd22b2b44b191205",
)
TARGET_FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-std=c11",
    "-O2", "-ffreestanding", "-ffunction-sections", "-fdata-sections",
    "-fno-builtin", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-Wall", "-Wextra", "-Werror",
]


class AmbiqGpuPatchGetGlyphCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ambiq-get-glyph-")
        temporary = Path(cls.temporary.name)
        library = temporary / ("glyph.dylib" if sys.platform == "darwin" else "glyph.so")
        subprocess.run(
            [
                cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
                str(SOURCE), str(FIXTURE),
                *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ),
                "-o", str(library),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_ambiq_glyph_force_size.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ambiq_glyph_lookup.argtypes = [ctypes.c_char_p]
        cls.lib.open_cfw_test_ambiq_glyph_lookup.restype = ctypes.c_uint32
        cls.target = temporary / "glyph.o"
        subprocess.run(
            [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_ambiq_glyph_reset()

    def test_all_four_utf8_widths_select_expected_glyph(self) -> None:
        cases = {
            b"A": 100,
            b"C": 102,
            "¢".encode(): 200,
            "€".encode(): 300,
            "😀".encode(): 400,
            "😁".encode(): 401,
        }
        for encoded, expected in cases.items():
            with self.subTest(encoded=encoded):
                self.assertEqual(self.lib.open_cfw_test_ambiq_glyph_lookup(encoded), expected)

    def test_missing_codepoint_walks_to_null_glyph_sentinel(self) -> None:
        for encoded in (b"D", "£".encode(), "🙂".encode()):
            with self.subTest(encoded=encoded):
                self.assertEqual(self.lib.open_cfw_test_ambiq_glyph_lookup(encoded), 0)

    def test_invalid_size_and_zero_codepoint_return_null(self) -> None:
        for forced in (0, 5, 0xFFFFFFFF - 1):
            with self.subTest(forced=forced):
                self.lib.open_cfw_test_ambiq_glyph_force_size(forced)
                self.assertEqual(self.lib.open_cfw_test_ambiq_glyph_lookup(b"A"), 0)
        self.lib.open_cfw_test_ambiq_glyph_force_size(1)
        self.assertEqual(self.lib.open_cfw_test_ambiq_glyph_lookup(b"\0"), 0)

    def test_public_section_dwarf_line_and_only_relocation_are_exact(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        item = next(
            row for row in manifest["gpu_patch"]["binary_recovery"]["function_census"]
            if row["function"] == "lv_ambiq_get_glyph"
        )
        self.assertEqual(
            (item["section_size"], item["symbol_size"], item["section_sha256"]),
            PUBLIC_SECTION,
        )
        self.assertEqual(item["source_line"], 818)
        self.assertEqual(item["relocation_count"], 1)
        self.assertEqual(item["relocation_targets"], ["utf8_codepoint_size"])

    def test_target_layout_assertions_compile_and_body_is_relocation_free(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.target)
        section = next(item for item in sections if item["name"] == ".text." + FUNCTION)
        self.assertGreater(int(section["size"]), 0)
        relocations = [
            item for item in sections
            if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
            and int(item["size"]) != 0
        ]
        self.assertEqual(relocations, [])
        self.assertTrue(data.startswith(b"\x7fELF"))

    def test_candidate_is_independently_named_and_production_excluded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: GPL-3.0-only", source)
        self.assertNotIn("\nlv_ambiq_get_glyph(", source)
        production = "\n".join(
            path.read_text(errors="replace")
            for path in (
                ROOT / "components/apollo_main/core_overlay/overlay.json",
                ROOT / "manifests/g2-2.2.6.10-core-source.json",
            )
        )
        self.assertNotIn(FUNCTION, production)


if __name__ == "__main__":
    unittest.main()
