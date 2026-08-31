#!/usr/bin/env python3
"""Hostile forwarding and target ABI gates for the isolated Apollo HAL adapter."""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_apollo_hal_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_apollo_hal_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class ApolloHALProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-apollo-hal-")
        suffix = "provider.dylib" if sys.platform == "darwin" else "provider.so"
        library = Path(cls.temporary.name) / suffix
        command = [
            cls.clang, "-std=c11", "-O2", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510"),
            "-I", str(ROOT / "third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include"),
            "-I", str(ROOT / "third_party/cmsis-core/CMSIS/Core/Include"),
            str(SOURCE), str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(library),
        ]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.test_apollo_hal_clean.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_apollo_hal_clean.restype = ctypes.c_uint32
        cls.lib.test_apollo_hal_invalidate.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_apollo_hal_invalidate.restype = ctypes.c_uint32
        cls.lib.test_apollo_hal_enable.argtypes = [ctypes.c_uint32]
        cls.lib.test_apollo_hal_enable.restype = ctypes.c_uint32
        cls.lib.test_apollo_hal_disable.argtypes = [ctypes.c_uint32]
        cls.lib.test_apollo_hal_disable.restype = ctypes.c_uint32
        cls.lib.test_apollo_hal_enabled.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_apollo_hal_enabled.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.test_apollo_hal_reset()

    def value(self, name: str) -> int:
        return int(getattr(self.lib, name)()) & 0xFFFFFFFF

    def test_cache_clean_forwards_exact_range_and_null(self) -> None:
        self.assertEqual(self.lib.test_apollo_hal_clean(0x20001234, 0xFEDC, 0), 0xA1000001)
        self.assertEqual(self.value("test_apollo_hal_clean_calls"), 1)
        self.assertEqual(self.value("test_apollo_hal_cache_pointer_is_null"), 0)
        self.assertEqual(self.value("test_apollo_hal_last_cache_start"), 0x20001234)
        self.assertEqual(self.value("test_apollo_hal_last_cache_size"), 0xFEDC)

        self.assertEqual(self.lib.test_apollo_hal_clean(0xFFFFFFFF, 0xFFFFFFFF, 1), 0xA1000001)
        self.assertEqual(self.value("test_apollo_hal_clean_calls"), 2)
        self.assertEqual(self.value("test_apollo_hal_cache_pointer_is_null"), 1)

    def test_cache_invalidate_canonicalizes_bool_without_dereferencing_null(self) -> None:
        self.assertEqual(
            self.lib.test_apollo_hal_invalidate(0x60000000, 0x80000000, 7, 0),
            0xA1000002,
        )
        self.assertEqual(self.value("test_apollo_hal_last_cache_start"), 0x60000000)
        self.assertEqual(self.value("test_apollo_hal_last_cache_size"), 0x80000000)
        self.assertEqual(self.value("test_apollo_hal_last_clean_selector"), 1)

        self.assertEqual(self.lib.test_apollo_hal_invalidate(0, 0, 0, 1), 0xA1000002)
        self.assertEqual(self.value("test_apollo_hal_invalidate_calls"), 2)
        self.assertEqual(self.value("test_apollo_hal_cache_pointer_is_null"), 1)
        self.assertEqual(self.value("test_apollo_hal_last_clean_selector"), 0)

    def test_power_adapters_preserve_full_enum_value_and_return_code(self) -> None:
        # The authenticated Apollo510 enum is one byte under -fshort-enums.
        self.assertEqual(self.lib.test_apollo_hal_enable(0xFE), 0xA1000003)
        self.assertEqual(self.value("test_apollo_hal_enable_calls"), 1)
        self.assertEqual(self.value("test_apollo_hal_last_enable_peripheral"), 0xFE)
        self.assertEqual(self.lib.test_apollo_hal_disable(0xFF), 0xA1000004)
        self.assertEqual(self.value("test_apollo_hal_disable_calls"), 1)
        self.assertEqual(self.value("test_apollo_hal_last_disable_peripheral"), 0xFF)

    def test_enabled_forwards_exact_pointer_including_null(self) -> None:
        self.assertEqual(self.lib.test_apollo_hal_enabled(0xFD, 1, 0), 0xA1000005)
        self.assertEqual(self.value("test_apollo_hal_enabled_calls"), 1)
        self.assertEqual(self.value("test_apollo_hal_last_enabled_peripheral"), 0xFD)
        self.assertEqual(self.value("test_apollo_hal_enabled_pointer_is_exact"), 1)
        self.assertEqual(self.value("test_apollo_hal_enabled_output"), 1)

        self.assertEqual(self.lib.test_apollo_hal_enabled(0xFC, 0, 1), 0xA1000005)
        self.assertEqual(self.value("test_apollo_hal_enabled_calls"), 2)
        self.assertEqual(self.value("test_apollo_hal_last_enabled_peripheral"), 0xFC)
        self.assertEqual(self.value("test_apollo_hal_enabled_pointer_is_exact"), 1)
        self.assertEqual(self.value("test_apollo_hal_enabled_output"), 0x5A)

    def test_checked_target_artifact_and_admission_bounds_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_apollo_hal_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-apollo-hal-provider.o",
            "size": 11_320,
            "sha256": "04504e7e026eb53a08a187e037269d0f42a2e818842fc5320710c2a5952a06b7",
        })
        self.assertEqual(provider["required_exports"], [
            "am_hal_cachectrl_dcache_clean",
            "am_hal_cachectrl_dcache_invalidate",
            "am_hal_pwrctrl_periph_disable",
            "am_hal_pwrctrl_periph_enable",
            "am_hal_pwrctrl_periph_enabled",
        ])
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["fixed_address_import_count"], 11)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])


if __name__ == "__main__":
    unittest.main()
