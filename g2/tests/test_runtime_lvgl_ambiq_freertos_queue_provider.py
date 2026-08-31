#!/usr/bin/env python3
"""Hostile ABI gates for the isolated LVGL/Nema FreeRTOS queue provider."""

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
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_freertos_queue_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_freertos_queue_provider_host.c"
ABI_FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_freertos_queue_provider_abi.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class FreeRTOSQueueProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-freertos-provider-")
        suffix = "provider.dylib" if sys.platform == "darwin" else "provider.so"
        library = Path(cls.temporary.name) / suffix
        subprocess.run([
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            str(SOURCE), str(FIXTURE),
            *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
            "-o", str(library),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.test_freertos_provider_create.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.test_freertos_provider_create.restype = ctypes.c_uint32
        cls.lib.test_freertos_provider_give.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.test_freertos_provider_give.restype = ctypes.c_int32
        cls.lib.test_freertos_provider_take.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.test_freertos_provider_take.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.test_freertos_provider_reset()

    def value(self, name: str) -> int:
        return int(getattr(self.lib, name)()) & 0xFFFFFFFF

    def test_binary_semaphore_create_forwards_exact_public_abi(self) -> None:
        self.assertEqual(self.lib.test_freertos_provider_create(1, 0, 3), 1)
        self.assertEqual(self.value("test_freertos_provider_create_calls"), 1)
        self.assertEqual(self.value("test_freertos_provider_last_length"), 1)
        self.assertEqual(self.value("test_freertos_provider_last_item_size"), 0)
        self.assertEqual(self.value("test_freertos_provider_last_queue_type"), 3)

    def test_create_zero_and_arithmetic_wrap_fail_closed(self) -> None:
        self.assertEqual(self.lib.test_freertos_provider_create(0, 0, 3), 0)
        self.assertEqual(self.lib.test_freertos_provider_create(0x80000000, 2, 0), 0)
        self.assertEqual(self.lib.test_freertos_provider_create(0xFFFFFFB0, 1, 0), 0)
        self.assertEqual(self.value("test_freertos_provider_create_calls"), 0)

        # Exact highest payload that still leaves the authenticated 0x50-byte Queue_t.
        self.assertEqual(self.lib.test_freertos_provider_create(0xFFFFFFAF, 1, 0), 1)
        self.assertEqual(self.value("test_freertos_provider_create_calls"), 1)
        self.assertEqual(self.value("test_freertos_provider_last_length"), 0xFFFFFFAF)

    def test_give_forwards_queue_and_optional_woken_pointer(self) -> None:
        self.assertEqual(self.lib.test_freertos_provider_give(0, 0), -17)
        self.assertEqual(self.value("test_freertos_provider_give_calls"), 1)
        self.assertEqual(self.value("test_freertos_provider_give_queue_is_exact"), 1)
        self.assertEqual(self.value("test_freertos_provider_woken_pointer_is_nonnull"), 1)
        self.assertEqual(self.value("test_freertos_provider_woken_value"), 1)

        self.assertEqual(self.lib.test_freertos_provider_give(0, 1), -17)
        self.assertEqual(self.value("test_freertos_provider_give_calls"), 2)
        self.assertEqual(self.value("test_freertos_provider_woken_pointer_is_null"), 1)

    def test_null_queue_operations_fail_closed_without_provider_call(self) -> None:
        self.assertEqual(self.lib.test_freertos_provider_give(1, 0), 0)
        self.assertEqual(self.lib.test_freertos_provider_take(1, 0xFFFFFFFF), 0)
        self.assertEqual(self.value("test_freertos_provider_give_calls"), 0)
        self.assertEqual(self.value("test_freertos_provider_take_calls"), 0)
        self.assertEqual(self.value("test_freertos_provider_woken_value"), 0x5A5A5A5A)

    def test_take_forwards_full_tick_range_and_return_code(self) -> None:
        self.assertEqual(self.lib.test_freertos_provider_take(0, 0xFFFFFFFF), -23)
        self.assertEqual(self.value("test_freertos_provider_take_calls"), 1)
        self.assertEqual(self.value("test_freertos_provider_take_queue_is_exact"), 1)
        self.assertEqual(self.value("test_freertos_provider_last_ticks"), 0xFFFFFFFF)

    def test_manifest_pins_closed_target_provider(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_freertos_queue_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-freertos-queue-provider.o",
            "size": 6_404,
            "sha256": "926b0597a2d78ea441151b2c21cfc813be29bb246606b2a6b0c5d84e5b175608",
        })
        self.assertEqual(provider["required_exports"], [
            "xQueueGenericCreate", "xQueueGiveFromISR", "xQueueSemaphoreTake",
        ])
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["fixed_address_import_count"], 27)
        upstream = provider["authenticated_upstream"]
        self.assertEqual(
            upstream["commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(upstream["license"], "MIT")
        self.assertTrue(upstream["target_prototypes_compatible"])
        self.assertEqual(upstream["abi_probe_artifact"], {
            "path": "lvgl_ambiq_freertos_queue_provider_abi.o",
            "size": 912,
            "sha256": "6e8878ec3fd45b9be8f409c13497953819f01dce665fb28bb3e5ae37cfa3622f",
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])
        self.assertEqual(report["missing_provider_count"], 11)

    def test_public_freertos_prototypes_are_target_type_compatible(self) -> None:
        output = Path(self.temporary.name) / "freertos-abi.o"
        subprocess.run([
            self.clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16", "-std=gnu11",
            "-ffreestanding", "-fshort-enums", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors"),
            "-I", str(ROOT / "third_party/freertos-kernel/include"),
            "-I", str(ROOT / "third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure"),
            "-c", str(ABI_FIXTURE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
