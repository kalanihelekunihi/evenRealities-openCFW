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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_fifo_4232c8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_fifo_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareFifoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-fifo.dylib" if sys.platform == "darwin" else "hw-fifo.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.read = cls.lib.open_cfw_bootloader_hw_fifo_read_4232c8
        cls.read.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.read.restype = ctypes.c_uint32
        cls.write = cls.lib.open_cfw_bootloader_hw_fifo_write_42330e
        cls.write.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.write.restype = ctypes.c_uint32
        cls.drain = cls.lib.open_cfw_bootloader_hw_fifo_drain_423342
        cls.drain.argtypes = [ctypes.POINTER(Instance)]
        cls.drain.restype = ctypes.c_uint32
        cls.status_values = (ctypes.c_uint32 * 64).in_dll(cls.lib, "open_cfw_hwfifo_host_status_values")
        cls.read_values = (ctypes.c_uint32 * 64).in_dll(cls.lib, "open_cfw_hwfifo_host_read_values")
        cls.write_values = (ctypes.c_uint32 * 64).in_dll(cls.lib, "open_cfw_hwfifo_host_write_values")
        for name in ("status_length", "read_length", "status_position", "read_position", "write_count", "last_index"):
            setattr(cls, name, ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwfifo_host_" + name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for array in (self.status_values, self.read_values, self.write_values):
            for index in range(64): array[index] = 0
        for name in ("status_length", "read_length", "status_position", "read_position", "write_count", "last_index"):
            getattr(self, name).value = 0

    @staticmethod
    def instance(index: int = 0) -> Instance:
        value = Instance()
        for shift in range(4): value.bytes[0x28 + shift] = (index >> (8 * shift)) & 0xFF
        return value

    def test_authenticated_bodies_literal_callers_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = ((0x132C8, 0x1330E, "7b349febf39ea04555da281af9f701f56cc26ed342d170a42e8e57db46798792"), (0x1330E, 0x13342, "06f979293ecda1e5d879a567c915acfbcb6fcf74cbc3d29660b53343a508a7ab"), (0x13342, 0x13350, "f070519f752fc88363405ec74084da9733180bb83f63db34d3ae7945719bd9af"))
        for start, end, expected in spans:
            self.assertEqual(hashlib.sha256(blob[start:end]).hexdigest(), expected)
        self.assertEqual(int.from_bytes(blob[0x13764:0x13768], "little"), 0x40039000)
        self.assertEqual(blob[0x13350:0x13358].hex(), "38b58ab004002500")

    def test_read_collects_available_low_bytes_and_reports_count(self) -> None:
        self.status_values[0:3] = (0, 0, 1 << 4)
        self.status_length.value = 2
        self.read_values[0:2] = (0x41, 0x42)
        self.read_length.value = 2
        output = (ctypes.c_uint8 * 4)()
        count = ctypes.c_uint32(99)
        self.assertEqual(self.read(ctypes.byref(self.instance(3)), output, 4, ctypes.byref(count)), 0)
        self.assertEqual((bytes(output[:2]), count.value, self.last_index.value), (b"AB", 2, 3))

    def test_read_error_bits_fail_closed_and_drain_discards_until_empty(self) -> None:
        self.status_values[0:2] = (0, 1 << 4)
        self.status_length.value = 1
        self.read_values[0] = 0x100
        count = ctypes.c_uint32(99)
        output = (ctypes.c_uint8 * 1)()
        self.assertEqual(self.read(ctypes.byref(self.instance()), output, 1, ctypes.byref(count)), 0x08000000)
        self.assertEqual(count.value, 0)
        self.status_position.value = self.read_position.value = 0
        self.read_values[0] = 0x55
        self.assertEqual(self.drain(ctypes.byref(self.instance())), 0)
        self.assertEqual(self.read_position.value, 1)

    def test_write_stops_when_full_and_preserves_exact_count(self) -> None:
        self.status_values[0:3] = (0, 0, 1 << 5)
        self.status_length.value = 2
        data = (ctypes.c_uint8 * 4)(1, 2, 3, 4)
        count = ctypes.c_uint32(99)
        self.assertEqual(self.write(ctypes.byref(self.instance(2)), data, 4, ctypes.byref(count)), 0)
        self.assertEqual((list(self.write_values[:2]), self.write_count.value, count.value, self.last_index.value), ([1, 2], 2, 2, 2))

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwfifo.o"))], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
