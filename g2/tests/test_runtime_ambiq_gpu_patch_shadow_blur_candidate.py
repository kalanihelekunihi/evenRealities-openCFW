#!/usr/bin/env python3
"""Qualify the production-excluded Ambiq GPU two-pass shadow candidate."""

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
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_gpu_patch_shadow_blur_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_gpu_patch_shadow_blur_candidate_host.c"
AUDIT = ROOT / "docs/research/ambiq-gpu-patch-shadow-blur-source-candidate-audit.md"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
PUBLIC_SECTION = (
    668,
    "cea1f3cb0efe575af62a887e8daec87479bc94807355f14df019cf02613faef8",
)

TARGET_FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffreestanding",
    "-ffunction-sections", "-fdata-sections", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-Wall", "-Wextra", "-Werror",
]


class AmbiqGpuPatchShadowBlurCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ambiq-shadow-")
        temporary = Path(cls.temporary.name)
        library = temporary / ("shadow.dylib" if sys.platform == "darwin" else "shadow.so")
        subprocess.run(
            [
                cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
                str(SOURCE), str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(library),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_ambiq_shadow_blur_run.argtypes = [ctypes.c_int32] * 2 + [ctypes.c_uint32] * 2
        cls.lib.open_cfw_test_ambiq_shadow_blur_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_shadow_blur_operation.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ambiq_shadow_blur_operation.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_shadow_blur_argument.argtypes = [ctypes.c_uint32] * 2
        cls.lib.open_cfw_test_ambiq_shadow_blur_argument.restype = ctypes.c_uint32
        cls.target = temporary / "shadow.o"
        subprocess.run(
            [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def records(self) -> list[tuple[int, tuple[int, ...]]]:
        return [
            (
                self.lib.open_cfw_test_ambiq_shadow_blur_operation(index),
                tuple(
                    self.lib.open_cfw_test_ambiq_shadow_blur_argument(index, argument)
                    for argument in range(8)
                ),
            )
            for index in range(self.lib.open_cfw_test_ambiq_shadow_blur_count())
        ]

    def test_odd_width_exact_two_pass_command_stream(self) -> None:
        self.lib.open_cfw_test_ambiq_shadow_blur_run(8, 3, 2, 4)
        records = self.records()
        operations = [record[0] for record in records]
        self.assertEqual(
            operations,
            [1, 2, 3, 3, 3, 1, 2, 4, 5, 1, 6, 7, 3, 3,
             1, 2, 3, 3, 3, 1, 2, 4, 5, 1, 6, 7, 3, 3, 3, 8],
        )
        self.assertEqual(records[0][1][:4], (1, 4, 2, 0xFFFFFFFF))
        self.assertEqual(records[1][1][:4], (0, 0, 11, 11))
        self.assertEqual(records[2][1], (1, 1, 8, 8, 0, 0, 8, 8))
        self.assertEqual(records[3][1], (0, 1, 1, 8, 0, 0, 1, 8))
        self.assertEqual(records[4][1], (9, 1, 1, 8, 7, 0, 1, 8))
        self.assertEqual(records[5][1][:4], (1, 2, 0xFF, 0xFFFFFFFF))
        self.assertEqual(records[9][1][:4], (0x08000101, 2, 4, 0xFFFFFFFF))
        self.assertEqual(records[10][1][:5], (0, 0, 0, 85, 0x55000000))
        self.assertEqual(records[11][1][0], 0x55000000)
        self.assertEqual(records[12][1], (0, 0, 8, 8, 0, 1, 8, 8))
        self.assertEqual(records[13][1], (0, 0, 8, 8, 1, 1, 8, 8))
        self.assertEqual(records[16][1], (1, 1, 8, 8, 0, 0, 8, 8))
        self.assertEqual(records[17][1], (1, 0, 8, 1, 0, 0, 8, 1))
        self.assertEqual(records[18][1], (1, 9, 8, 1, 0, 7, 8, 1))
        self.assertEqual(records[26][1], (0, 0, 8, 8, 1, 0, 8, 8))
        self.assertEqual(records[27][1], (0, 0, 8, 8, 1, 1, 8, 8))
        self.assertEqual(records[28][1], (0, 0, 8, 8, 1, 2, 8, 8))

    def test_even_width_uses_asymmetric_leading_edge(self) -> None:
        self.lib.open_cfw_test_ambiq_shadow_blur_run(7, 4, 1, 3)
        records = self.records()
        self.assertEqual(records[1][1][:4], (0, 0, 11, 11))
        self.assertEqual(records[2][1], (1, 1, 7, 7, 0, 0, 7, 7))
        self.assertEqual(records[4][1], (8, 1, 2, 7, 5, 0, 2, 7))
        self.assertEqual(records[10][1][3], 63)
        first_loop = [record[1] for record in records[12:15]]
        self.assertEqual([args[4] for args in first_loop], [0, 1, 2])
        second_loop = [record[1] for record in records[27:31]]
        self.assertEqual([args[5] for args in second_loop], [0, 1, 2, 3])

    def test_width_one_preserves_zero_horizontal_and_one_vertical_sample(self) -> None:
        self.lib.open_cfw_test_ambiq_shadow_blur_run(5, 1, 1, 2)
        records = self.records()
        self.assertEqual(len(records), 26)
        self.assertEqual(sum(record[0] == 3 for record in records), 7)
        self.assertEqual(records[-2][1], (0, 0, 5, 5, 0, 0, 5, 5))
        self.assertEqual([record[1][3] for record in records if record[0] == 6], [255, 255])

    def test_exact_public_section_and_manifest_status_are_pinned(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        census = {
            item["function"]: item
            for item in manifest["gpu_patch"]["binary_recovery"]["function_census"]
        }
        shadow = census["lv_ambiq_shadow_blur_corner"]
        self.assertEqual((shadow["section_size"], shadow["section_sha256"]), PUBLIC_SECTION)
        self.assertEqual(shadow["symbol_size"], 668)
        self.assertEqual(shadow["source_line"], 383)
        self.assertEqual(shadow["relocation_count"], 39)
        self.assertEqual(shadow["source_status"], "bounded-clean-room-candidate")

    def test_target_candidate_is_relocation_free_and_hard_float(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.target)
        section = next(
            item for item in sections
            if item["name"] == ".text.open_cfw_ambiq_gpu_shadow_blur_corner_candidate"
        )
        self.assertGreater(int(section["size"]), 0)
        relocations = [
            item for item in sections
            if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
            and int(item["size"]) != 0
        ]
        self.assertEqual(relocations, [])
        self.assertTrue(data.startswith(b"\x7fELF"))

    def test_candidate_is_independent_documented_and_production_excluded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: GPL-3.0-only", source)
        self.assertNotIn("void lv_ambiq_shadow_blur_corner(", source)
        self.assertIn("two-pass", AUDIT.read_text())
        production = "\n".join(
            path.read_text(errors="replace")
            for path in (
                ROOT / "components/apollo_main/core_overlay/overlay.json",
                ROOT / "manifests/g2-2.2.6.10-core-source.json",
            )
        )
        self.assertNotIn("open_cfw_ambiq_gpu_shadow_blur_corner_candidate", production)


if __name__ == "__main__":
    unittest.main()
