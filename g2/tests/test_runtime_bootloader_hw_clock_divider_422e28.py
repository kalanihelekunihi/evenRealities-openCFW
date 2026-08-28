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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_clock_divider_422e28.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_clock_divider_host.c"
REFERENCES = (0, 24_000_000, 12_000_000, 6_000_000, 3_000_000, 48_000_000, 49_152_000)


class BootloaderHardwareClockDividerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / (
            "hw-clock.dylib" if sys.platform == "darwin" else "hw-clock.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
                "-Wall", "-Wextra", "-Werror", str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(output),
            ],
            check=True,
            capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.configure = cls.lib.open_cfw_bootloader_hw_clock_divider_422e28
        cls.configure.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.configure.restype = ctypes.c_uint32
        cls.registers = ((ctypes.c_uint32 * 32) * 4).in_dll(cls.lib, "open_cfw_hwcd_host_registers")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for bank in self.registers:
            for index in range(32):
                bank[index] = 0

    def test_authenticated_body_caller_pools_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x12E28:0x12EE2]
        self.assertEqual(len(body), 186)
        self.assertEqual(hashlib.sha256(body).hexdigest(), "4a9a62072ca502be40f4c3ecf68b1ba3871f34be9258aa90ffdca7526f8378c4")
        self.assertEqual(blob[0x131A8:0x131AC].hex(), "fff73efe")
        self.assertEqual(blob[0x12E74:0x12E78].hex(), "fff702fd")
        self.assertEqual(blob[0x12EE2:0x12EEA].hex(), "7cb504000e000025")
        self.assertEqual(int.from_bytes(blob[0x13440:0x13444], "little"), 0x40039000)
        self.assertEqual(int.from_bytes(blob[0x136FC:0x13700], "little"), 3_000_000)
        self.assertEqual(
            tuple(int.from_bytes(blob[offset:offset + 4], "little") for offset in range(0x13834, 0x13850, 4)),
            (49_152_000, 0x08000003, 48_000_000, 24_000_000, 12_000_000, 6_000_000, 0x08000002),
        )

    def test_invalid_clock_modes_zero_output_without_register_writes(self) -> None:
        for bank, mode in ((0, 0), (3, 7)):
            self.registers[bank][12] = mode << 4
            self.registers[bank][9] = 0xAAAAAAAA
            self.registers[bank][10] = 0x55555555
            actual = ctypes.c_uint32(0xDEADBEEF)
            self.assertEqual(self.configure(bank, 48_000, ctypes.byref(actual)), 0x08000002)
            self.assertEqual(actual.value, 0)
            self.assertEqual((self.registers[bank][9], self.registers[bank][10]), (0xAAAAAAAA, 0x55555555))

    def test_all_reference_modes_program_exact_integer_fraction_and_actual(self) -> None:
        requests = (44_100, 48_000, 96_000, 96_000, 8_000, 32_000)
        for mode, request in zip(range(1, 7), requests):
            bank = (mode - 1) % 4
            reference = REFERENCES[mode]
            self.registers[bank][12] = (mode << 4) | 0xF000000F
            actual = ctypes.c_uint32()
            self.assertEqual(self.configure(bank, request, ctypes.byref(actual)), 0)
            divisor = request << 4
            integer = reference // divisor
            fraction = ((reference << 6) // divisor) - (integer << 6)
            expected_actual = reference // ((integer << 4) + (fraction >> 2))
            self.assertEqual((self.registers[bank][9], self.registers[bank][10]), (integer, fraction))
            self.assertEqual(actual.value, expected_actual)

    def test_integer_zero_returns_status_three_without_programming(self) -> None:
        self.registers[2][12] = 1 << 4
        self.registers[2][9] = 7
        self.registers[2][10] = 9
        actual = ctypes.c_uint32(1)
        self.assertEqual(self.configure(2, 24_000_001, ctypes.byref(actual)), 0x08000003)
        self.assertEqual(actual.value, 0)
        self.assertEqual((self.registers[2][9], self.registers[2][10]), (7, 9))

    def test_bank_selection_and_exact_divisible_request(self) -> None:
        for bank in range(4):
            self.registers[bank][12] = 5 << 4
            actual = ctypes.c_uint32()
            self.assertEqual(self.configure(bank, 3_000_000, ctypes.byref(actual)), 0)
            self.assertEqual((self.registers[bank][9], self.registers[bank][10]), (1, 0))
            self.assertEqual(actual.value, 3_000_000)
            for other in range(4):
                if other != bank:
                    self.assertEqual((self.registers[other][9], self.registers[other][10]), (0, 0))
            self.registers[bank][9] = 0
            self.registers[bank][10] = 0

    def test_zero_or_wrapped_divisor_fails_closed_in_host_model(self) -> None:
        self.registers[0][12] = 6 << 4
        for request in (0, 0x10000000):
            actual = ctypes.c_uint32(5)
            self.assertEqual(self.configure(0, request, ctypes.byref(actual)), 0x08000003)
            self.assertEqual(actual.value, 0)

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
                        str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwcd.o")),
                    ],
                    check=True,
                    capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
