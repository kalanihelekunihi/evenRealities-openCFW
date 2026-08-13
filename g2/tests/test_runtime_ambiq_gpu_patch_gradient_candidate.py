#!/usr/bin/env python3
"""Qualify the production-excluded two-stop Ambiq gradient candidate."""

from __future__ import annotations

import ctypes
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_gpu_patch_gradient_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_gpu_patch_gradient_candidate_host.c"
AUDIT = ROOT / "docs/research/ambiq-gpu-patch-gradient-source-candidate-audit.md"
ORACLE = ROOT / "tools/emulate_ambiq_gpu_patch_gradient.py"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
PUBLIC_SECTION = (
    1_416,
    "5870d79c49ee8bd0dfa4b5bf8f6f39b04ed45148c0c00b774467149292d83ae4",
)
STOCK_SPAN = (
    "0x005FA238",
    "0x005FA7C0",
    "82d1ae24eff6da055d251b067ce54e002940cd90a8283af0063381448ea6dc93",
)

TARGET_FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffreestanding",
    "-ffunction-sections", "-fdata-sections", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-Wall", "-Wextra", "-Werror",
]


class Color(ctypes.Structure):
    _fields_ = [
        ("red", ctypes.c_float),
        ("green", ctypes.c_float),
        ("blue", ctypes.c_float),
        ("alpha", ctypes.c_float),
    ]


class AmbiqGpuPatchGradientCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ambiq-gradient-")
        temporary = Path(cls.temporary.name)
        library = temporary / ("gradient.dylib" if sys.platform == "darwin" else "gradient.so")
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
        cls.lib.open_cfw_test_ambiq_gradient_run.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(Color),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.lib.open_cfw_test_ambiq_gradient_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_gradient_operation.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ambiq_gradient_operation.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_gradient_argument.argtypes = [ctypes.c_uint32] * 2
        cls.lib.open_cfw_test_ambiq_gradient_argument.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_gradient_value.argtypes = [ctypes.c_uint32] * 2
        cls.lib.open_cfw_test_ambiq_gradient_value.restype = ctypes.c_float
        cls.target = temporary / "gradient.o"
        subprocess.run(
            [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_candidate(
        self, stops_values: list[float], colors_values: list[tuple[float, float, float, float]]
    ) -> list[tuple[int, tuple[int, ...], tuple[float, ...]]]:
        stops = (ctypes.c_float * len(stops_values))(*stops_values)
        colors = (Color * len(colors_values))(*(Color(*color) for color in colors_values))
        self.lib.open_cfw_test_ambiq_gradient_run(len(stops_values), stops, colors, 2, 64)
        return [
            (
                self.lib.open_cfw_test_ambiq_gradient_operation(index),
                tuple(self.lib.open_cfw_test_ambiq_gradient_argument(index, arg) for arg in range(5)),
                tuple(self.lib.open_cfw_test_ambiq_gradient_value(index, value) for value in range(12)),
            )
            for index in range(self.lib.open_cfw_test_ambiq_gradient_count())
        ]

    def test_endpoint_pair_matches_exact_object_oracle_trace(self) -> None:
        records = self.run_candidate([0.0, 1.0], [(255, 0, 0, 255), (0, 0, 255, 255)])
        self.assertEqual([record[0] for record in records], [1, 2, 3, 4, 5, 6, 4, 8, 6, 8, 6, 4, 9])
        self.assertEqual(records[0][1][0], 2)
        self.assertEqual(records[1][1][:4], (0, 0, 64, 1))
        self.assertEqual(records[2][1][:4], (1, 2, 0xFFFFFFFF, 0xFFFFFFFF))
        expected = (255.0, 0.0, 0.0, 255.0, -4.047618865966797, 0.0,
                    0.0, 0.0, 4.047618865966797, 0.0, 0.0, 0.0)
        for actual, wanted in zip(records[4][2], expected):
            self.assertAlmostEqual(actual, wanted, places=5)
        self.assertEqual(records[5][1], (0, 0, 64, 1, 0xFFFFFFFF))
        self.assertEqual(records[7][1], (255, 0, 0, 255, 0xFF0000FF))
        self.assertEqual(records[8][1], (0, 0, 1, 1, 0xFF0000FF))
        self.assertEqual(records[10][1], (63, 0, 1, 1, 0x0000FFFF))

    def test_implicit_endpoints_match_three_exact_oracle_segments(self) -> None:
        records = self.run_candidate([0.25, 0.75], [(10, 20, 30, 40), (110, 120, 130, 140)])
        gradients = [record for record in records if record[0] == 5]
        fills = [record for record in records if record[0] == 6]
        self.assertEqual(len(gradients), 3)
        self.assertEqual([record[1][:4] for record in fills[:3]], [(0, 0, 16, 1), (16, 0, 32, 1), (48, 0, 16, 1)])
        self.assertEqual(gradients[0][2][:4], (10.0, 20.0, 30.0, 40.0))
        for actual, wanted in zip(
            gradients[1][2],
            (10.79365062713623, 20.793651580810547, 30.793651580810547,
             40.79365158081055, 3.174603223800659, 0.0,
             3.174603223800659, 0.0, 3.174603223800659, 0.0,
             3.174603223800659, 0.0),
        ):
            self.assertAlmostEqual(actual, wanted, places=5)
        self.assertEqual(gradients[2][2][:4], (110.0, 120.0, 130.0, 140.0))

    def test_descending_pair_uses_exact_black_to_white_fallback(self) -> None:
        records = self.run_candidate([0.75, 0.5], [(10, 20, 30, 40), (50, 60, 70, 80)])
        self.assertEqual([record[0] for record in records], [1, 2, 3, 4, 7, 6, 4, 9])
        self.assertEqual(records[4][1][:4], (0, 0, 64, 1))
        self.assertEqual(records[4][2], (0.0, 0.0, 0.0, 0.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0))
        self.assertEqual(records[5][1], (0, 0, 64, 1, 0xFFFFFFFF))

    def test_duplicate_stop_preserves_zero_width_infinite_slope_segment(self) -> None:
        records = self.run_candidate([0.5, 0.5], [(10, 20, 30, 40), (50, 60, 70, 80)])
        gradients = [record for record in records if record[0] == 5]
        fills = [record for record in records if record[0] == 6]
        self.assertEqual(len(gradients), 3)
        self.assertTrue(all(math.isinf(value) for value in gradients[1][2][4::2]))
        self.assertEqual(fills[1][1][:4], (32, 0, 0, 1))

    def test_exact_binary_stock_and_two_stop_boundary_are_pinned(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        recovery = manifest["gpu_patch"]["binary_recovery"]
        census = {item["function"]: item for item in recovery["function_census"]}
        gradient = census["lv_ambiq_gradient_create"]
        self.assertEqual((gradient["section_size"], gradient["section_sha256"]), PUBLIC_SECTION)
        self.assertEqual((gradient["source_line"], gradient["relocation_count"]), (138, 16))
        self.assertEqual(gradient["source_status"], "bounded-clean-room-candidate")
        self.assertEqual(recovery["gradient"]["stock_span"]["start"], STOCK_SPAN[0])
        self.assertEqual(recovery["gradient"]["stock_span"]["end_exclusive"], STOCK_SPAN[1])
        self.assertEqual(recovery["gradient"]["stock_span"]["sha256"], STOCK_SPAN[2])
        self.assertIn("EXPECTED_SECTION_SHA256", ORACLE.read_text())

    def test_target_candidate_has_no_external_relocations(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        _, sections = apollo_overlay.parse_elf32(self.target)
        text_sections = [
            item for item in sections
            if str(item["name"]).startswith(".text.") and int(item["size"]) > 0
        ]
        text_indexes = {int(item["index"]) for item in text_sections}
        relocation_sections = [
            item for item in sections
            if int(item["type"]) == 9 and int(item["size"]) != 0
            and int(item["info"]) in text_indexes
        ]
        self.assertTrue(any("gradient_create_candidate" in str(item["name"]) for item in text_sections))
        self.assertEqual(relocation_sections, [])

    def test_candidate_is_independent_documented_and_production_excluded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: GPL-3.0-only", source)
        self.assertNotIn("void lv_ambiq_gradient_create(", source)
        self.assertIn("two-stop", AUDIT.read_text())
        production = "\n".join(
            path.read_text(errors="replace")
            for path in (
                ROOT / "components/apollo_main/core_overlay/overlay.json",
                ROOT / "manifests/g2-2.2.6.10-core-source.json",
            )
        )
        self.assertNotIn("open_cfw_ambiq_gpu_gradient_create_candidate", production)


if __name__ == "__main__":
    unittest.main()
