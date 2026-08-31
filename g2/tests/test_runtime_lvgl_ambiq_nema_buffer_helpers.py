#!/usr/bin/env python3
"""Hostile-input and target ABI gates for the two G2 Nema buffer helpers."""

from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.c"
CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_nema_buffer_helpers_host_config.h"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_nema_buffer_helpers_host.c"
ANALYZER = ROOT / "tools/analyze_g2_nema_hal.py"


class NemaBufferHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="nema-buffer-helpers-")
        suffix = "helpers.dylib" if sys.platform == "darwin" else "helpers.so"
        library = Path(cls.temporary.name) / suffix
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-include", str(CONFIG),
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/nema-sdk-headers/port"),
            "-I", str(ROOT / "third_party/nema-sdk-headers/headers/include/tsi/NemaGFX"),
            "-I", str(ROOT / "third_party/nema-sdk-headers/headers/include/tsi/common"),
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510"),
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include"),
            "-I", str(ROOT / "third_party/cmsis-core/CMSIS/Core/Include"),
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu"),
            str(SOURCE), str(FIXTURE),
            *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ),
            "-o", str(library),
        ]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.test_nema_helpers_set_heap.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_nema_helpers_within.argtypes = [
            ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_nema_helpers_within.restype = ctypes.c_uint32
        cls.lib.test_nema_helpers_invalidate.argtypes = [
            ctypes.c_int32, ctypes.c_uint32, ctypes.c_int32,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.test_nema_helpers_reset()

    def within(self, pool: int, start: int, length: int) -> bool:
        return bool(self.lib.test_nema_helpers_within(pool, start, length))

    def test_exact_pool_mapping_and_closed_intervals(self) -> None:
        self.assertTrue(self.within(0, 0x20010000, 0x1000))
        self.assertTrue(self.within(1, 0x20011000, 0))
        self.assertTrue(self.within(2, 0x60000100, 0x100))
        self.assertTrue(self.within(3, 0x200207FF, 1))
        self.assertTrue(self.within(99, 0x20010000, 1))  # Stock default: render.
        self.assertFalse(self.within(2, 0x5FFFFFFF, 1))
        self.assertFalse(self.within(3, 0x20020800, 1))

    def test_range_and_descriptor_wraparound_fail_closed(self) -> None:
        self.assertFalse(self.within(0, 0xFFFFFFFF, 0x20011001))
        self.assertFalse(self.within(0, 0x20010FFF, 2))
        self.lib.test_nema_helpers_set_heap(0, 0xFFFFFFF0, 0x20, 1)
        self.assertFalse(self.within(0, 0xFFFFFFF0, 1))
        self.lib.test_nema_helpers_set_heap(0, 0x20010000, 0, 1)
        self.assertTrue(self.within(0, 0x20010000, 0))
        self.assertFalse(self.within(0, 0x20010000, 1))

    def test_invalidate_uses_physical_range_and_never_requests_clean(self) -> None:
        self.lib.test_nema_helpers_invalidate(0, 0x20010120, 0x80)
        self.assertEqual(self.lib.test_nema_helpers_call_count(), 1)
        self.assertEqual(self.lib.test_nema_helpers_last_start(), 0x20010120)
        self.assertEqual(self.lib.test_nema_helpers_last_size(), 0x80)
        self.assertEqual(self.lib.test_nema_helpers_last_clean(), 0)

    def test_invalidate_hostile_inputs_do_not_reach_cache_hal(self) -> None:
        self.lib.test_nema_helpers_invalidate_null()
        self.lib.test_nema_helpers_invalidate(0, 0x20010000, -1)
        self.lib.test_nema_helpers_invalidate(0, 0xFFFFFFFF, 0x100)
        self.lib.test_nema_helpers_invalidate(0, 0x20010FFF, 2)
        self.lib.test_nema_helpers_invalidate(2, 0x60000000, 0x20)  # Non-cacheable.
        self.assertEqual(self.lib.test_nema_helpers_call_count(), 0)

    def test_stock_helper_bytes_and_descriptor_addresses_are_authenticated(self) -> None:
        spec = importlib.util.spec_from_file_location("nema_hal_helper_audit", ANALYZER)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.analyze()
        rows = {row["function"]: row for row in report["stock"]["functions"]}
        self.assertEqual(rows["nema_buffer_invalidate"]["bytes"], 46)
        self.assertEqual(rows["nema_buffer_is_within_pool"]["bytes"], 36)
        self.assertEqual(report["stock"]["heap_descriptors"], [
            0x20000354, 0x20000370, 0x20000338,
        ])


if __name__ == "__main__":
    unittest.main()
