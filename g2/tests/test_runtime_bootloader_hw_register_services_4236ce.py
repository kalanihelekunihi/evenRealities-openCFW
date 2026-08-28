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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_register_services_4236ce.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_register_services_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareRegisterServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hwrs.dylib" if sys.platform == "darwin" else "hwrs.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.reg_or = cls.lib.open_cfw_bootloader_hw_register_or_4236ce
        cls.reg_or.argtypes = [ctypes.POINTER(Instance), ctypes.c_uint32]
        cls.reg_or.restype = ctypes.c_uint32
        cls.write = cls.lib.open_cfw_bootloader_hw_register_write_423700
        cls.write.argtypes = [ctypes.POINTER(Instance), ctypes.c_uint32]
        cls.write.restype = ctypes.c_uint32
        cls.query = cls.lib.open_cfw_bootloader_hw_register_query_42372a
        cls.query.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        cls.query.restype = ctypes.c_uint32
        cls.registers = ((ctypes.c_uint32 * 18) * 4).in_dll(cls.lib, "open_cfw_hwrs_host_registers")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for bank in self.registers:
            for index in range(18):
                bank[index] = 0

    @staticmethod
    def instance(bank: int = 0, identity: int = 0x01EA9E06) -> Instance:
        result = Instance()
        for offset, value in ((0, identity), (0x28, bank)):
            for shift in range(4):
                result.bytes[offset + shift] = (value >> (8 * shift)) & 0xFF
        return result

    def test_authenticated_bodies_literals_and_boundaries(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x136CE, 0x136FA, "8d9b9730cd66a1de3b8886d2a29f71dc72f72bb61a252a10a45227dc309756b7"),
            (0x13700, 0x1372A, "9af271cb1237dcd8aa9147adad8a333ce2c70532fba9e090bc9f1b8a2fa390b7"),
            (0x1372A, 0x13764, "d2a8d31be1192d40a4240d1f392856b268a0005cf45bcc7f3fb769c0e17d518b"),
        )
        for start, end, expected in spans:
            self.assertEqual(hashlib.sha256(blob[start:end]).hexdigest(), expected)
        self.assertEqual(blob[0x136FA:0x13700].hex(), "0000c0c62d00")
        self.assertEqual(int.from_bytes(blob[0x13764:0x13768], "little"), 0x40039000)
        self.assertEqual(blob[0x1377C:0x13784].hex(), "f8b504000e002500")

    def test_register_or_preserves_existing_bits_and_selects_bank(self) -> None:
        instance = self.instance(2)
        self.registers[2][0x38 // 4] = 0x5000
        self.assertEqual(self.reg_or(ctypes.byref(instance), 0x0210), 0)
        self.assertEqual(self.registers[2][0x38 // 4], 0x5210)

    def test_write_and_dual_query_registers(self) -> None:
        instance = self.instance(1)
        self.assertEqual(self.write(ctypes.byref(instance), 0xA5A55A5A), 0)
        self.assertEqual(self.registers[1][0x44 // 4], 0xA5A55A5A)
        self.registers[1][0x3C // 4] = 0x11223344
        self.registers[1][0x40 // 4] = 0x55667788
        output = ctypes.c_uint32()
        self.assertEqual(self.query(ctypes.byref(instance), ctypes.byref(output), 0x100), 0)
        self.assertEqual(output.value, 0x11223344)
        self.assertEqual(self.query(ctypes.byref(instance), ctypes.byref(output), 0x101), 0)
        self.assertEqual(output.value, 0x55667788)

    def test_invalid_identity_returns_two_without_register_mutation(self) -> None:
        instance = self.instance(identity=0x01EA9E07)
        output = ctypes.c_uint32(0xDEADBEEF)
        self.assertEqual(self.reg_or(ctypes.byref(instance), 0xFFFFFFFF), 2)
        self.assertEqual(self.write(ctypes.byref(instance), 0xFFFFFFFF), 2)
        self.assertEqual(self.query(ctypes.byref(instance), ctypes.byref(output), 0), 2)
        self.assertEqual(output.value, 0xDEADBEEF)
        self.assertTrue(all(value == 0 for bank in self.registers for value in bank))

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwrs.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
