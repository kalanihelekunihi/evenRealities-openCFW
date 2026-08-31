#!/usr/bin/env python3
"""Semantic, hostile-input, and ownership gates for the cache-free radius mask."""

from __future__ import annotations

import ctypes
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tools/build_g2_lvgl_ambiq_backend.py"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_sw_mask_cache_free_host.c"
READINESS = ROOT / "tools/manifests/g2-lvgl-ambiq-backend-readiness.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("lvgl_ambiq_mask_builder", BUILDER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CacheFreeRadiusMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.cc = shutil.which("cc") or shutil.which("clang")
        if cls.cc is None:
            raise unittest.SkipTest("host C compiler is unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="opencfw-lvgl-radius-mask-")
        cls.stage = Path(cls.temp.name)
        cls.lvgl = cls.builder._stage_tree(cls.stage)
        cls.candidate = cls._build_library(reference=False)
        cls.reference = cls._build_library(reference=True)
        cls._configure_library(cls.candidate)
        cls._configure_library(cls.reference)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    @classmethod
    def _build_library(cls, *, reference: bool) -> ctypes.CDLL:
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        output = cls.stage / (("reference" if reference else "candidate") + suffix)
        common = [
            cls.cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-fvisibility=hidden",
            "-DLV_CONF_SKIP=1",
            "-DLV_USE_OS=LV_OS_NONE",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM",
            "-DLV_USE_LOG=0",
            "-DLV_USE_FREETYPE=0",
            "-I",
            str(cls.lvgl),
            "-I",
            str(cls.lvgl / "src"),
        ]
        if reference:
            source = cls.lvgl / "src/draw/sw/lv_draw_sw_mask.c"
            shutil.copy2(cls.builder.SW_MASK_UPSTREAM, source)
            compile_flags = [
                "-DLV_DRAW_SW_COMPLEX=1",
                "-DOPEN_CFW_SW_MASK_REFERENCE=1",
                "-ffunction-sections",
                "-fdata-sections",
            ]
        else:
            source = cls.lvgl / "src/draw/ambiq/lvgl_ambiq_sw_mask_cache_free.c"
            compile_flags = [
                "-DLV_DRAW_SW_COMPLEX=0",
                "-DOPEN_CFW_SW_MASK_REFERENCE=0",
            ]
        if sys.platform == "darwin":
            link_flags = ["-dynamiclib"] + (["-Wl,-dead_strip"] if reference else [])
        else:
            link_flags = ["-shared", "-fPIC", "-Wl,--gc-sections"]
        subprocess.run(
            [
                *common,
                *compile_flags,
                str(source),
                str(FIXTURE),
                *link_flags,
                "-o",
                str(output),
            ],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        return ctypes.CDLL(str(output))

    @staticmethod
    def _configure_library(library: ctypes.CDLL) -> None:
        library.open_cfw_test_mask_allocator_reset.argtypes = [ctypes.c_size_t]
        for name in (
            "open_cfw_test_mask_allocation_attempts",
            "open_cfw_test_mask_allocations_live",
            "open_cfw_test_mask_bytes_live",
            "open_cfw_test_mask_peak_bytes",
        ):
            getattr(library, name).restype = ctypes.c_size_t
        library.open_cfw_test_mask_render.argtypes = [
            *([ctypes.c_int32] * 9),
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8),
        ]
        library.open_cfw_test_mask_render.restype = ctypes.c_int
        library.open_cfw_test_mask_null_and_double_free.restype = ctypes.c_int

    @staticmethod
    def _render(library: ctypes.CDLL, case: tuple[int, ...]) -> tuple[int, bytes]:
        length = case[8]
        output = (ctypes.c_uint8 * length)()
        library.open_cfw_test_mask_allocator_reset(ctypes.c_size_t(-1).value)
        result = library.open_cfw_test_mask_render(*case, output)
        return result, bytes(output)

    def test_authenticated_reference_and_checked_provider_are_pinned(self) -> None:
        report = self.builder.audit_inputs()
        boundary = report["cache_free_radius_mask"]
        self.assertEqual(boundary["upstream"]["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(boundary["upstream"]["size"], 43_443)
        self.assertEqual(boundary["upstream"]["git_blob_sha1"], "0e1a17a67f15e44fe294a26b18f7be5da7c2acb2")
        self.assertEqual(boundary["upstream"]["sha256"], "8a5075210d3a59c4fa7ea00e5675205a6a2e7e8e98305c26045c30c2e77846a6")
        self.assertEqual(boundary["provider"]["exports"], [
            "lv_draw_sw_mask_radius_init", "lv_draw_sw_mask_free_param",
        ])
        self.assertFalse(boundary["provider"]["global_cache_dependency"])
        self.assertEqual(boundary["provider"]["arm_parameter_size"], 36)
        self.assertEqual(boundary["provider"]["arm_parameter_offsets"], {
            "cfg": 8, "radius": 24, "circle": 32,
        })
        contract = boundary["provider"]["host_verification_contract"]
        self.assertEqual(contract["authenticated_reference_parity_cases"], 1_505)
        self.assertEqual(contract["allocation_failure_sites"], 3)
        self.assertEqual(contract["peak_allocation_upper_bound_bytes"], 3_296)
        self.assertEqual(json.loads(READINESS.read_text(encoding="utf-8")), report)

    def test_cache_free_raster_matches_authenticated_upstream(self) -> None:
        cases: list[tuple[int, ...]] = [
            (0, 0, 31, 15, 0, 0, -4, 0, 40, 255),
            (0, 0, 7, 7, 1, 0, 0, 0, 8, 255),
            (-7, 4, 24, 35, 16, 0, -12, 4, 48, 255),
            (-7, 4, 24, 35, 16, 1, -12, 35, 48, 173),
            (10, -20, 85, 27, 999, 0, 0, -20, 100, 91),
        ]
        rng = random.Random(0x5109_3000)
        for _ in range(1_500):
            x1 = rng.randint(-80, 80)
            y1 = rng.randint(-50, 50)
            width = rng.randint(1, 120)
            height = rng.randint(1, 96)
            cases.append((
                x1, y1, x1 + width - 1, y1 + height - 1,
                rng.randint(-8, 160), rng.randrange(2),
                rng.randint(x1 - 40, x1 + width + 40),
                rng.randint(y1 - 16, y1 + height + 16),
                rng.randint(1, 192), rng.randrange(256),
            ))

        for index, case in enumerate(cases):
            with self.subTest(index=index, case=case):
                self.assertEqual(
                    self._render(self.candidate, case),
                    self._render(self.reference, case),
                )
                self.assertEqual(self.candidate.open_cfw_test_mask_allocations_live(), 0)
                self.assertEqual(self.candidate.open_cfw_test_mask_bytes_live(), 0)

    def test_all_allocation_failures_degrade_without_leak_or_write(self) -> None:
        case = (0, 0, 31, 31, 8, 0, 0, 0, 32, 0xA7)
        for failed_attempt in range(3):
            with self.subTest(failed_attempt=failed_attempt):
                output = (ctypes.c_uint8 * 32)()
                self.candidate.open_cfw_test_mask_allocator_reset(failed_attempt)
                result = self.candidate.open_cfw_test_mask_render(*case, output)
                self.assertEqual(result, 0)  # LV_DRAW_SW_MASK_RES_TRANSP
                self.assertEqual(bytes(output), bytes([0xA7]) * 32)
                self.assertEqual(self.candidate.open_cfw_test_mask_allocations_live(), 0)
                self.assertEqual(self.candidate.open_cfw_test_mask_bytes_live(), 0)

    def test_hostile_coordinates_lengths_and_lifecycle_are_bounded(self) -> None:
        self.candidate.open_cfw_test_mask_allocator_reset(ctypes.c_size_t(-1).value)
        self.assertEqual(self.candidate.open_cfw_test_mask_null_and_double_free(), 0)

        storage = (ctypes.c_uint8 * 64)(*([0xCC] * 64))
        interior = ctypes.cast(ctypes.byref(storage, 16), ctypes.POINTER(ctypes.c_uint8))
        result = self.candidate.open_cfw_test_mask_render(
            0, 0, 31, 31, 16, 0, -8, 0, 32, 0xFF, interior,
        )
        self.assertIn(result, (0, 1, 2))
        self.assertEqual(bytes(storage[:16]), bytes([0xCC]) * 16)
        self.assertEqual(bytes(storage[48:]), bytes([0xCC]) * 16)

        hostile = [
            (-(2**31), -(2**31), 2**31 - 1, 2**31 - 1, 2**31 - 1, 0, 0, 0, 16, 0x5A),
            (10, 10, 9, 9, 5, 0, 0, 0, 16, 0x5A),
            (0, 0, 31, 31, 16, 0, 2**31 - 1, 0, 16, 0x5A),
            (0, 0, 31, 31, 16, 1, -(2**31), 0, 16, 0x5A),
        ]
        for case in hostile:
            with self.subTest(case=case):
                result, output = self._render(self.candidate, case)
                self.assertIn(result, (0, 1))
                self.assertEqual(len(output), 16)
                self.assertEqual(self.candidate.open_cfw_test_mask_allocations_live(), 0)

        self.candidate.open_cfw_test_mask_allocator_reset(ctypes.c_size_t(-1).value)
        self.assertEqual(
            self.candidate.open_cfw_test_mask_render(
                0, 0, 31, 31, 8, 0, 0, 0, 0, 0xFF, None,
            ),
            1,  # LV_DRAW_SW_MASK_RES_FULL_COVER
        )
        self.assertEqual(self.candidate.open_cfw_test_mask_allocations_live(), 0)

    def test_g2_maximum_visible_radius_has_linear_bounded_peak(self) -> None:
        case = (0, 0, 575, 287, 144, 0, 0, 0, 576, 255)
        result, _ = self._render(self.candidate, case)
        self.assertEqual(result, 2)  # LV_DRAW_SW_MASK_RES_CHANGED
        self.assertEqual(self.candidate.open_cfw_test_mask_allocation_attempts(), 3)
        self.assertLessEqual(self.candidate.open_cfw_test_mask_peak_bytes(), 22 * 144 + 128)
        self.assertEqual(self.candidate.open_cfw_test_mask_allocations_live(), 0)
        self.assertEqual(self.candidate.open_cfw_test_mask_bytes_live(), 0)


if __name__ == "__main__":
    unittest.main()
