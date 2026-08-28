from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_service_dispatch_42377c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_service_dispatch_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareServiceDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hwsd.dylib" if sys.platform == "darwin" else "hwsd.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.dispatch = cls.lib.open_cfw_bootloader_hw_service_dispatch_42377c
        cls.dispatch.argtypes = [ctypes.POINTER(Instance), ctypes.c_uint32]
        cls.dispatch.restype = ctypes.c_uint32
        names = (
            "bank50_value", "status_value", "shutdown_count",
            "clear_secondary_count", "clear_primary_count",
            "secondary_progress_count", "primary_progress_count",
            "callback_count", "callback_status", "callback_context",
            "status_index", "status_flags",
        )
        for name in names:
            setattr(cls, name, ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwsd_host_" + name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for name in (
            "bank50_value", "status_value", "shutdown_count",
            "clear_secondary_count", "clear_primary_count",
            "secondary_progress_count", "primary_progress_count",
            "callback_count", "callback_status", "callback_context",
            "status_index", "status_flags",
        ):
            getattr(self, name).value = 0

    @staticmethod
    def write32(instance: Instance, offset: int, value: int) -> None:
        for shift in range(4):
            instance.bytes[offset + shift] = (value >> (8 * shift)) & 0xFF

    @staticmethod
    def read32(instance: Instance, offset: int) -> int:
        return sum(int(instance.bytes[offset + shift]) << (8 * shift) for shift in range(4))

    def instance(self, identity: int = 0x01EA9E06, bank: int = 0) -> Instance:
        result = Instance()
        self.write32(result, 0, identity)
        self.write32(result, 0x28, bank)
        return result

    def test_authenticated_body_pools_and_boundaries(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(
            hashlib.sha256(blob[0x1377C:0x1382C]).hexdigest(),
            "2cbdef7278215a0c7195f2f1be71e0c9f945d4647d3d1bc1d15365cd6a52ad61",
        )
        self.assertEqual(hashlib.sha256(blob[0x13764:0x1377C]).hexdigest(), "2a5b0ce73bc2295f563559c798d0262265fa3010bee7c38c18a29ef3d75786ee")
        self.assertEqual(hashlib.sha256(blob[0x1382C:0x13864]).hexdigest(), "1c53b412e3fbb0cb88a21c22d1e2338353506516a1f4f531c09b24b49463db29")

    def test_invalid_type_returns_two_without_services(self) -> None:
        instance = self.instance(identity=0x01EA9E07)
        self.assertEqual(self.dispatch(ctypes.byref(instance), 0xFFFFFFFF), 2)
        self.assertEqual(self.shutdown_count.value + self.primary_progress_count.value, 0)

    def test_inactive_instance_routes_progress_and_latches_flag(self) -> None:
        instance = self.instance()
        self.assertEqual(self.dispatch(ctypes.byref(instance), 0x71), 1)
        self.assertEqual((self.secondary_progress_count.value, self.primary_progress_count.value, instance.bytes[0xDE]), (1, 1, 1))

    def test_active_instance_completes_mirror_callback_and_cleanup(self) -> None:
        instance = self.instance(bank=3)
        instance.bytes[0x11B] = 1
        self.write32(instance, 0xE4, 0x2000)
        self.write32(instance, 0xE8, 1)
        self.write32(instance, 0xF0, 1)
        self.write32(instance, 0xF4, 0xAABBCCDD)
        self.bank50_value.value = 0x1234
        self.status_value.value = 0x08000005
        flags = (1 << 6) | (1 << 11) | (1 << 12)
        self.assertEqual(self.dispatch(ctypes.byref(instance), flags), 1)
        self.assertEqual(self.read32(instance, 0xEC), 0x1DCC)
        self.assertEqual((self.shutdown_count.value, self.clear_secondary_count.value, self.clear_primary_count.value), (1, 1, 1))
        self.assertEqual((self.callback_count.value, self.callback_status.value, self.callback_context.value), (1, 0x08000005, 0xAABBCCDD))
        self.assertEqual((self.status_index.value, self.status_flags.value), (3, flags))
        self.assertEqual((instance.bytes[0x11B], self.read32(instance, 0xF0)), (0, 0))

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwsd.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
