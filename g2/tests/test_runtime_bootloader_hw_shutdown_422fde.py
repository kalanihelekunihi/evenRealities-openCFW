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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_shutdown_422fde.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_shutdown_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class BootloaderHardwareShutdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-shutdown.dylib" if sys.platform == "darwin" else "hw-shutdown.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.shutdown = cls.lib.open_cfw_bootloader_hw_shutdown_422fde
        cls.shutdown.argtypes = [ctypes.POINTER(Instance)]
        cls.shutdown.restype = None
        row = ctypes.c_uint32 * (0x40 // 4)
        cls.registers = (row * 4).in_dll(cls.lib, "open_cfw_hwsh_host_registers")
        for name in ("delay_count", "delay_ticks", "clear_count", "shutdown_count", "release_count", "order", "clear_order", "shutdown_order", "release_order", "clear_register", "shutdown_register", "release_register"):
            setattr(cls, name, ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwsh_host_" + name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for bank in self.registers:
            for index in range(len(bank)):
                bank[index] = 0
        for name in ("delay_count", "delay_ticks", "clear_count", "shutdown_count", "release_count", "order", "clear_order", "shutdown_order", "release_order", "clear_register", "shutdown_register", "release_register"):
            getattr(self, name).value = 0

    @staticmethod
    def put32(instance: Instance, offset: int, value: int) -> None:
        for shift in range(4):
            instance.bytes[offset + shift] = (value >> (8 * shift)) & 0xFF

    def instance(self, index: int = 0, divisor: int = 100) -> Instance:
        value = Instance()
        self.put32(value, 0x28, index)
        self.put32(value, 0x30, divisor)
        return value

    def test_authenticated_body_caller_literals_providers_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12FDE:0x1308E]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (176, "7241a63d66335d340551094ebc58d5aaf07bb7e88bb254c4e2dc8c9975701107"))
        self.assertEqual(blob[0x137C8:0x137CC].hex(), "fff709fc")
        self.assertEqual(int.from_bytes(blob[0x13764:0x13768], "little"), 0x40039000)
        self.assertEqual(int.from_bytes(blob[0x13858:0x1385C], "little"), 10000000)
        self.assertEqual(hashlib.sha256(blob[0xD1C0:0xD210]).hexdigest(), "c336d5c93475c6521bab00509a8ad8aaa1078b3bdc313ae43107777520af1895")
        self.assertEqual(hashlib.sha256(blob[0x12D4C:0x12D7A]).hexdigest(), "c037d8b13a19cbc61ee88209bac5b8e5ef628aed1363424bb66a80ce2cf24559")
        self.assertEqual(hashlib.sha256(blob[0x13342:0x13350]).hexdigest(), "f070519f752fc88363405ec74084da9733180bb83f63db34d3ae7945719bd9af")
        self.assertEqual(blob[0x1308E:0x13096].hex(), "f8b504000f00002c")

    def test_enabled_path_quiesces_before_providers_and_restores_only_required_bits(self) -> None:
        instance = self.instance()
        instance.bytes[0x11B] = 1
        original = 0xA5000000 | 0x4000 | 0x800 | 0x200 | 0x40
        self.registers[0][0x30 // 4] = original
        self.shutdown(ctypes.byref(instance))
        during = original & ~(0x4000 | 0x800 | 0x200)
        self.assertEqual((self.clear_register.value, self.shutdown_register.value, self.release_register.value), (during, during, during))
        self.assertEqual(self.registers[0][0x30 // 4], (original & ~0x800) | 0x4000 | 0x200)
        self.assertEqual((self.clear_order.value, self.shutdown_order.value, self.release_order.value), (1, 2, 3))

    def test_disabled_path_does_not_invent_enable_or_clear_bit_eleven(self) -> None:
        instance = self.instance(index=2)
        original = 0x800 | 0x200 | 0x55
        self.registers[2][0x30 // 4] = original
        self.shutdown(ctypes.byref(instance))
        self.assertEqual(self.registers[2][0x30 // 4], original)
        self.assertEqual((self.clear_count.value, self.shutdown_count.value, self.release_count.value), (0, 1, 1))

    def test_active_status_delays_by_ten_million_over_instance_rate_plus_one(self) -> None:
        instance = self.instance(divisor=125)
        self.registers[0][0x18 // 4] = 1 << 3
        self.shutdown(ctypes.byref(instance))
        self.assertEqual((self.delay_count.value, self.delay_ticks.value), (1, 80001))
        self.registers[0][0x18 // 4] = 0
        self.shutdown(ctypes.byref(instance))
        self.assertEqual(self.delay_count.value, 1)

    def test_all_four_banks_are_selected_by_instance_index(self) -> None:
        for index in range(4):
            instance = self.instance(index=index)
            self.registers[index][0x30 // 4] = 0x4000 | 0x800
            self.shutdown(ctypes.byref(instance))
            self.assertEqual(self.registers[index][0x30 // 4], 0x4000 | 0x200)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwsh.o"))], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
