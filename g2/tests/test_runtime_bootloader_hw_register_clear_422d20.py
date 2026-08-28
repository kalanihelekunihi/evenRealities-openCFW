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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_register_clear_422d20.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_register_clear_host.c"


class BootloaderHardwareRegisterClearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-clear.dylib" if sys.platform == "darwin" else "hw-clear.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.clear20 = cls.lib.open_cfw_bootloader_hw_register_clear_422d20
        cls.clear4c = cls.lib.open_cfw_bootloader_hw_register_clear_422d4c
        cls.clear20.argtypes = cls.clear4c.argtypes = [ctypes.c_void_p]
        cls.reset = cls.lib.open_cfw_hwrc_host_reset; cls.reset.argtypes = [ctypes.c_uint32]
        cls.registers = ((ctypes.c_uint32 * 32) * 4).in_dll(cls.lib, "open_cfw_hwrc_host_registers")

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    @staticmethod
    def instance(index):
        raw = (ctypes.c_uint8 * 0x11C)()
        raw[0x28:0x2C] = index.to_bytes(4, "little")
        return raw

    def test_authenticated_bodies_callers_pools_and_successor(self):
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x12D20:0x12D4C]).hexdigest(), "74e3724ef4d0b99489a9c3ca805c8c3c8603f6cc8bd483acf3d836829980e0d9")
        self.assertEqual(hashlib.sha256(blob[0x12D4C:0x12D7A]).hexdigest(), "c037d8b13a19cbc61ee88209bac5b8e5ef628aed1363424bb66a80ce2cf24559")
        self.assertEqual(int.from_bytes(blob[0x13440:0x13444], "little"), 0x40039000)
        self.assertEqual(int.from_bytes(blob[0x13764:0x13768], "little"), 0x40039000)
        self.assertEqual(blob[0x12D7A:0x12D7C], b"\x02\x00")

    def test_first_leaf_clears_output_and_two_control_bits_for_all_banks(self):
        for index in range(4):
            self.reset(0xFFFFFFFF); self.clear20(self.instance(index))
            self.assertEqual(self.registers[index][18], 0)
            self.assertEqual(self.registers[index][1], 0xFFFFFFCF)
            for other in range(4):
                if other != index: self.assertEqual(self.registers[other][18], 0xFFFFFFFF)

    def test_second_leaf_clears_output_control_and_low_twelve_bits(self):
        for index in range(4):
            self.reset(0xA5A5FFFF); self.clear4c(self.instance(index))
            self.assertEqual(self.registers[index][18], 0)
            self.assertEqual(self.registers[index][1], 0xA5A5FFDF)
            self.assertEqual(self.registers[index][20], 0xA5A5F000)

    def test_source_cross_compiles(self):
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hw-clear.o"))], check=True, capture_output=True)


if __name__ == "__main__": unittest.main()
