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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_descriptor_init_422dc6.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_descriptor_init_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareDescriptorInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / (
            "hw-descriptor.dylib" if sys.platform == "darwin" else "hw-descriptor.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(output),
            ],
            check=True,
            capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.initialize = cls.lib.open_cfw_bootloader_hw_descriptor_init_422dc6
        cls.initialize.argtypes = [
            ctypes.POINTER(Instance), ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.initialize.restype = ctypes.c_uint32
        cls.call_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwdi_host_call_count")
        cls.descriptors = (ctypes.c_size_t * 2).in_dll(cls.lib, "open_cfw_hwdi_host_descriptor")
        cls.buffers = (ctypes.c_uint32 * 2).in_dll(cls.lib, "open_cfw_hwdi_host_buffer")
        cls.enabled = (ctypes.c_uint32 * 2).in_dll(cls.lib, "open_cfw_hwdi_host_enabled")
        cls.values = (ctypes.c_uint32 * 2).in_dll(cls.lib, "open_cfw_hwdi_host_value")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.call_count.value = 0
        for values in (self.descriptors, self.buffers, self.enabled, self.values):
            for index in range(2):
                values[index] = 0

    @staticmethod
    def make_instance(header: int = 0x01EA9E06) -> Instance:
        instance = Instance()
        instance.bytes[:] = bytes([0xA5]) * 0x11C
        instance.bytes[0:4] = header.to_bytes(4, "little")
        return instance

    @staticmethod
    def words(instance: Instance, offset: int) -> tuple[int, ...]:
        raw = bytes(instance.bytes[offset:offset + 24])
        return tuple(int.from_bytes(raw[pos:pos + 4], "little") for pos in range(0, 24, 4))

    def test_authenticated_body_caller_literal_provider_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12DC6:0x12E28]
        self.assertEqual(len(body), 98)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "a8cfef03c32750c788e9226d7ed587f8c6e04a3a7202970f613c5737eb7a755a",
        )
        self.assertEqual(blob[0xF6AC:0xF6B0].hex(), "03f08bfb")
        self.assertEqual(int.from_bytes(blob[0x13830:0x13834], "little"), 0x01EA9E06)
        self.assertEqual(blob[0x12E28:0x12E2C].hex(), "2de9f041")
        self.assertEqual(
            hashlib.sha256(blob[0x175EA:0x17602]).hexdigest(),
            "142ce77e922601c4cf495ab896455263777d8088987c0f783477ea4aceff059f",
        )

    def test_invalid_instance_returns_two_without_mutation_or_calls(self) -> None:
        self.assertEqual(self.initialize(None, 1, 2, 3, 4), 2)
        instance = self.make_instance(0x12345678)
        before = bytes(instance.bytes)
        self.assertEqual(self.initialize(ctypes.byref(instance), 1, 2, 3, 4), 2)
        self.assertEqual(bytes(instance.bytes), before)
        self.assertEqual(self.call_count.value, 0)

    def test_absent_pairs_clear_flags_and_preserve_descriptors(self) -> None:
        instance = self.make_instance()
        before_first = bytes(instance.bytes[0x34:0x4C])
        before_second = bytes(instance.bytes[0x4C:0x64])
        for arguments in ((0, 1, 0, 1), (1, 0, 1, 0), (0, 0, 0, 0)):
            instance.bytes[0xDC] = 0xA5
            instance.bytes[0xDD] = 0x5A
            self.assertEqual(self.initialize(ctypes.byref(instance), *arguments), 0)
            self.assertEqual((instance.bytes[0xDC], instance.bytes[0xDD]), (0, 0))
            self.assertEqual(self.call_count.value, 0)
            self.assertEqual(bytes(instance.bytes[0x34:0x4C]), before_first)
            self.assertEqual(bytes(instance.bytes[0x4C:0x64]), before_second)

    def test_each_descriptor_is_initialized_with_exact_layout(self) -> None:
        instance = self.make_instance(0xFDEA9E06)
        self.assertEqual(
            self.initialize(ctypes.byref(instance), 0x11112222, 0x33334444, 0, 0), 0
        )
        self.assertEqual((instance.bytes[0xDC], instance.bytes[0xDD]), (1, 0))
        self.assertEqual(self.words(instance, 0x34), (0, 0, 0, 0x33334444, 1, 0x11112222))
        self.assertEqual(self.descriptors[0], ctypes.addressof(instance) + 0x34)
        self.assertEqual((self.buffers[0], self.enabled[0], self.values[0]), (0x11112222, 1, 0x33334444))

        self.call_count.value = 0
        instance = self.make_instance()
        self.assertEqual(
            self.initialize(ctypes.byref(instance), 0, 0, 0x55556666, 0x77778888), 0
        )
        self.assertEqual((instance.bytes[0xDC], instance.bytes[0xDD]), (0, 1))
        self.assertEqual(self.words(instance, 0x4C), (0, 0, 0, 0x77778888, 1, 0x55556666))
        self.assertEqual(self.descriptors[0], ctypes.addressof(instance) + 0x4C)

    def test_both_descriptors_are_initialized_in_order(self) -> None:
        instance = self.make_instance()
        self.assertEqual(self.initialize(ctypes.byref(instance), 10, 20, 30, 40), 0)
        self.assertEqual(self.call_count.value, 2)
        self.assertEqual(tuple(self.descriptors), (ctypes.addressof(instance) + 0x34, ctypes.addressof(instance) + 0x4C))
        self.assertEqual(tuple(self.buffers), (10, 30))
        self.assertEqual(tuple(self.enabled), (1, 1))
        self.assertEqual(tuple(self.values), (20, 40))

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [
                        compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                        "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                        "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
                        "-Werror", "-fno-ident", "-c", str(SOURCE), "-o",
                        str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwdi.o")),
                    ],
                    check=True,
                    capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
