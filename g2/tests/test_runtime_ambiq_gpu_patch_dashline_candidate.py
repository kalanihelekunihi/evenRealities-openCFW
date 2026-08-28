#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify the production-excluded Ambiq GPU dash-line candidate."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_gpu_patch_dashline_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_gpu_patch_dashline_candidate_host.c"
AUDIT = ROOT / "docs/research/ambiq-gpu-patch-dashline-source-candidate-audit.md"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
STOCK_START = 0x005F_A7C0
STOCK_END = 0x005F_A84A
STOCK_SHA256 = "aeda115cd2ea2bba4eee91b8510ec396bdb40b94184a16d51bfc86ba12ae70c0"
STOCK_CALLS = (
    (0x005F_A7E2, 0x004B_1516),
    (0x005F_A7F0, 0x0051_3924),
    (0x005F_A820, 0x0052_2A16),
    (0x005F_A82C, 0x0052_2AE0),
    (0x005F_A832, 0x0052_2A16),
    (0x005F_A83E, 0x0052_2AE0),
)
STOCK_TAIL = (0x005F_A846, 0x004B_1548)
STOCK_CONTEXT_LITERAL = (0x005F_A84C, 0x2007_4EFC)
PUBLIC_SECTION = (
    144,
    "9f465e5e7bc8c95a022a491d937c46f461071479093ad7f7101581c4a902f20b",
)

TARGET_FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffreestanding",
    "-ffunction-sections", "-fdata-sections", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-Wall", "-Wextra", "-Werror",
]


class AmbiqGpuPatchDashlineCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.image = OFFICIAL.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ambiq-dashline-")
        temporary = Path(cls.temporary.name)
        library = temporary / ("dashline.dylib" if sys.platform == "darwin" else "dashline.so")
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
        cls.lib.open_cfw_test_ambiq_dashline_run.argtypes = [ctypes.c_uint32] * 5
        cls.lib.open_cfw_test_ambiq_dashline_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_dashline_operation.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ambiq_dashline_operation.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_dashline_argument.argtypes = [ctypes.c_uint32] * 2
        cls.lib.open_cfw_test_ambiq_dashline_argument.restype = ctypes.c_uint32
        cls.target = temporary / "dashline.o"
        subprocess.run(
            [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def records(self) -> list[tuple[int, tuple[int, int, int, int]]]:
        return [
            (
                self.lib.open_cfw_test_ambiq_dashline_operation(index),
                tuple(
                    self.lib.open_cfw_test_ambiq_dashline_argument(index, argument)
                    for argument in range(4)
                ),
            )
            for index in range(self.lib.open_cfw_test_ambiq_dashline_count())
        ]

    def test_exact_effect_order_and_arguments(self) -> None:
        self.lib.open_cfw_test_ambiq_dashline_run(3, 2, 0xA1B2C3D4, 2, 17)
        self.assertEqual(
            self.records(),
            [
                (1, (2, 0, 0, 0)),
                (2, (0, 0, 17, 1)),
                (3, (1, 2, 0xFFFFFFFF, 0xFFFFFFFF)),
                (4, (0xA1B2C3D4, 0, 0, 0)),
                (5, (0, 0, 10, 1)),
                (4, (0, 0, 0, 0)),
                (5, (10, 0, 7, 1)),
                (6, (0, 0, 0, 0)),
            ],
        )

    def test_zero_dash_and_zero_gap_preserve_truncating_partition(self) -> None:
        for dash, gap, expected in ((0, 7, 0), (7, 0, 19), (1, 2, 6)):
            with self.subTest(dash=dash, gap=gap):
                self.lib.open_cfw_test_ambiq_dashline_run(dash, gap, 9, 1, 19)
                records = self.records()
                self.assertEqual(records[4][1][2], expected)
                self.assertEqual(records[6][1][0], expected)
                self.assertEqual(records[6][1][2], 19 - expected)

    def test_texture_id_uses_recovered_one_byte_abi(self) -> None:
        self.lib.open_cfw_test_ambiq_dashline_run(1, 1, 0, 0x102, 8)
        records = self.records()
        self.assertEqual(records[0][1][0], 2)
        self.assertEqual(records[2][1][1], 2)

    @staticmethod
    def decode_branch(image: bytes, address: int, link: bool) -> int | None:
        first, second = struct.unpack_from("<HH", image, address - BASE)
        if first & 0xF800 != 0xF000:
            return None
        expected = 0xD000 if link else 0x9000
        if second & 0xD000 != expected:
            return None
        sign = first >> 10 & 1
        j1, j2 = second >> 13 & 1, second >> 11 & 1
        i1, i2 = (~(j1 ^ sign)) & 1, (~(j2 ^ sign)) & 1
        immediate = (
            sign << 24 | i1 << 23 | i2 << 22 |
            (first & 0x3FF) << 12 | (second & 0x7FF) << 1
        )
        if sign:
            immediate -= 1 << 25
        return address + 4 + immediate

    def test_stock_iar_span_has_same_six_calls_tail_and_context(self) -> None:
        body = self.image[STOCK_START - BASE:STOCK_END - BASE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (138, STOCK_SHA256))
        calls = tuple(
            (address, target)
            for address in range(STOCK_START, STOCK_END - 3, 2)
            if (target := self.decode_branch(self.image, address, True)) is not None
        )
        self.assertEqual(calls, STOCK_CALLS)
        self.assertEqual(
            self.decode_branch(self.image, STOCK_TAIL[0], False), STOCK_TAIL[1]
        )
        self.assertEqual(
            struct.unpack_from("<I", self.image, STOCK_CONTEXT_LITERAL[0] - BASE)[0],
            STOCK_CONTEXT_LITERAL[1],
        )

    def test_exact_public_archive_section_and_dwarf_line_are_pinned(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        dashline = manifest["gpu_patch"]["binary_recovery"]["dashline"]
        self.assertEqual((dashline["section_size"], dashline["section_sha256"]), PUBLIC_SECTION)
        self.assertEqual(dashline["source_line"], 268)
        self.assertEqual(dashline["variables"], ["dash_buffer_size_pixel", "ratio", "w"])

    def test_target_candidate_is_relocation_free_and_hard_float(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.target)
        section = next(
            item for item in sections
            if item["name"] == ".text.open_cfw_ambiq_gpu_dashline_create_candidate"
        )
        self.assertGreater(int(section["size"]), 0)
        relocations = [
            item for item in sections
            if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
            and int(item["size"]) != 0
        ]
        self.assertEqual(relocations, [])
        self.assertTrue(data.startswith(b"\x7fELF"))

    def test_candidate_is_independent_and_production_excluded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", source)
        self.assertNotIn("void lv_ambiq_dashline_create(", source)
        production = "\n".join(
            path.read_text(errors="replace")
            for path in (
                ROOT / "components/apollo_main/core_overlay/overlay.json",
                ROOT / "manifests/g2-2.2.6.10-core-source.json",
            )
        )
        self.assertNotIn("open_cfw_ambiq_gpu_dashline_create_candidate", production)


if __name__ == "__main__":
    unittest.main()
