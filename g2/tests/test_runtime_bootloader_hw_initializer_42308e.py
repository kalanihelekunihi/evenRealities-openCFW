# SPDX-License-Identifier: MIT
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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_initializer_42308e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_initializer_host.c"


class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]


class Config(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x0D)]


class BootloaderHardwareInitializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / (
            "hw-initializer.dylib" if sys.platform == "darwin" else "hw-initializer.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.initialize = cls.lib.open_cfw_bootloader_hw_initializer_42308e
        cls.initialize.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(Config)]
        cls.initialize.restype = ctypes.c_uint32
        row = ctypes.c_uint32 * (0x40 // 4)
        cls.registers = (row * 4).in_dll(cls.lib, "open_cfw_hwinit_host_registers")
        for name in (
            "chip_revision",
            "global_control",
            "mode_count",
            "mode_value",
            "route_value",
            "clock_count",
            "clock_index",
            "clock_requested",
            "clock_actual",
            "clock_status",
        ):
            setattr(cls, name, ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwinit_host_" + name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for bank in self.registers:
            for index in range(len(bank)):
                bank[index] = 0
        for name in (
            "chip_revision",
            "global_control",
            "mode_count",
            "mode_value",
            "route_value",
            "clock_count",
            "clock_index",
            "clock_requested",
            "clock_actual",
            "clock_status",
        ):
            getattr(self, name).value = 0
        self.chip_revision.value = 0x22
        self.clock_actual.value = 12_345

    @staticmethod
    def put16(value: Instance | Config, offset: int, number: int) -> None:
        value.bytes[offset] = number & 0xFF
        value.bytes[offset + 1] = (number >> 8) & 0xFF

    @staticmethod
    def put32(value: Instance | Config, offset: int, number: int) -> None:
        for shift in range(4):
            value.bytes[offset + shift] = (number >> (8 * shift)) & 0xFF

    @staticmethod
    def get32(value: Instance, offset: int) -> int:
        return sum(int(value.bytes[offset + shift]) << (8 * shift) for shift in range(4))

    def values(self, *, index: int = 0, requested: int = 0x0016E361, mode: int = 0) -> tuple[Instance, Config]:
        instance = Instance()
        config = Config()
        self.put32(instance, 0, 0xA1EA9E06)
        self.put32(instance, 0x28, index)
        self.put32(config, 0, requested)
        config.bytes[0x0C] = mode
        return instance, config

    def test_authenticated_body_literals_and_two_source_providers(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x1308E:0x132C8]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (570, "80102228cb6a9eb99cd5bf229d5ca450331b2521a39e23e4e0671f7f928dbc46"),
        )
        self.assertEqual(int.from_bytes(blob[0x133E0:0x133E4], "little"), 0x01EA9E06)
        self.assertEqual(int.from_bytes(blob[0x13434:0x13438], "little"), 0x0016E361)
        self.assertEqual(int.from_bytes(blob[0x13438:0x1343C], "little"), 0x4002000C)
        self.assertEqual(int.from_bytes(blob[0x1343C:0x13440], "little"), 0x400201B0)
        self.assertEqual(int.from_bytes(blob[0x13440:0x13444], "little"), 0x40039000)
        self.assertEqual(body[0xE4:0xE8].hex(), "fff7bdf8")
        self.assertEqual(body[0x11A:0x11E].hex(), "fff73efe")

    def test_null_and_bad_instance_magic_return_two_without_side_effects(self) -> None:
        _, config = self.values()
        self.assertEqual(self.initialize(None, ctypes.byref(config)), 2)
        instance = Instance()
        self.put32(instance, 0, 0x01EA9E07)
        self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 2)
        self.assertEqual((self.mode_count.value, self.clock_count.value), (0, 0))
        self.assertTrue(all(value == 0 for bank in self.registers for value in bank))

    def test_invalid_mode_and_revision_gate_return_six_after_initial_register_latch(self) -> None:
        for mode, revision in ((2, 0x22), (255, 0x22), (1, 0x21)):
            self.setUp()
            self.chip_revision.value = revision
            instance, config = self.values(index=2, mode=mode)
            self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 6)
            self.assertEqual(self.registers[2][0x30 // 4], 8)
            self.assertEqual((self.mode_count.value, self.clock_count.value), (0, 0))

    def test_high_rate_programs_global_route_and_all_configured_register_fields(self) -> None:
        instance, config = self.values(index=2, mode=0)
        config.bytes[4] = 3
        config.bytes[5] = 1
        config.bytes[6] = 1
        self.put16(config, 8, 0x8402)
        config.bytes[0x0A] = 5
        config.bytes[0x0B] = 6
        self.global_control.value = 0x15
        self.registers[2][0x2C // 4] = 0xA5A500FF
        self.registers[2][0x34 // 4] = 0x5A5AFFFF
        self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 0)
        self.assertEqual(self.global_control.value, 0x15 | (0x00400000 << 2))
        self.assertEqual((instance.bytes[0x118], self.mode_value.value, self.route_value.value), (4, 4, 13))
        self.assertEqual((self.clock_index.value, self.clock_requested.value), (2, 0x0016E361))
        self.assertEqual(self.get32(instance, 0x30), 12_345)
        self.assertEqual(self.registers[2][0x30 // 4], 0x58 | 0x8402 | 0x301)
        self.assertEqual(self.registers[2][0x2C // 4], 0xA5A50000 | 0x7E)
        self.assertEqual(self.registers[2][0x34 // 4], (0x5A5AFFFF & ~0x3F) | 5 | (6 << 3))

    def test_low_rate_mode_one_clears_global_route_and_selects_mode_six(self) -> None:
        for index in range(4):
            self.setUp()
            self.global_control.value = 0x00400000 << index
            instance, config = self.values(index=index, requested=0x0016E360, mode=1)
            self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 0)
            self.assertEqual(self.global_control.value, 0)
            self.assertEqual((instance.bytes[0x118], self.mode_value.value), (6, 6))
            self.assertEqual(self.route_value.value, index + 11)
            self.assertEqual(self.registers[index][0x30 // 4] & 0x70, 0x60)

    def test_pre_revision_22_leaves_global_control_untouched(self) -> None:
        self.chip_revision.value = 0x20
        self.global_control.value = 0xA5A5A5A5
        instance, config = self.values(index=1)
        self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 0)
        self.assertEqual(self.global_control.value, 0xA5A5A5A5)

    def test_clock_error_propagates_before_post_divider_register_programming(self) -> None:
        instance, config = self.values(index=3, requested=1234, mode=0)
        self.clock_status.value = 0x08000003
        self.registers[3][0x2C // 4] = 0x11223344
        self.registers[3][0x34 // 4] = 0x55667788
        self.assertEqual(self.initialize(ctypes.byref(instance), ctypes.byref(config)), 0x08000003)
        self.assertEqual((self.mode_count.value, self.clock_count.value), (1, 1))
        self.assertEqual(self.registers[3][0x30 // 4], 0x18)
        self.assertEqual(self.registers[3][0x2C // 4], 0x11223344)
        self.assertEqual(self.registers[3][0x34 // 4], 0x55667788)

    def test_target_body_is_exact_except_for_the_two_declared_call_relocations(self) -> None:
        obj = Path(self.tmp.name) / "hwinit.o"
        raw = Path(self.tmp.name) / "hwinit.bin"
        compiler = "/usr/bin/clang"
        subprocess.run(
            [
                compiler,
                "-target",
                "arm-none-eabi",
                "-mcpu=cortex-m55",
                "-mthumb",
                "-Oz",
                "-ffreestanding",
                "-fno-builtin",
                "-ffunction-sections",
                "-fdata-sections",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-fno-ident",
                "-c",
                str(SOURCE),
                "-o",
                str(obj),
            ],
            check=True,
            capture_output=True,
        )
        objcopy = Path("/opt/homebrew/opt/llvm@22/bin/llvm-objcopy")
        if not objcopy.exists():
            self.skipTest("reviewed llvm-objcopy is unavailable")
        subprocess.run(
            [str(objcopy), "-O", "binary", "--only-section=.text.open_cfw_bootloader_hw_initializer_42308e", str(obj), str(raw)],
            check=True,
            capture_output=True,
        )
        compiled = raw.read_bytes()
        stock = OFFICIAL.read_bytes()[0x1308E:0x132C8]
        self.assertEqual((len(compiled), hashlib.sha256(compiled).hexdigest()), (570, "f08bff0cbc423ffc9408db313992c97fb4f181dadf7479f12820f8257e9a7826"))
        for offset in range(570):
            if offset not in {*range(0xE4, 0xE8), *range(0x11A, 0x11E)}:
                self.assertEqual(compiled[offset], stock[offset], f"byte {offset:#x}")

    def test_source_cross_compiles_with_both_reviewed_profiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [
                        compiler,
                        "-target",
                        "arm-none-eabi",
                        "-mcpu=cortex-m55",
                        "-mthumb",
                        "-Oz",
                        "-ffreestanding",
                        "-fno-builtin",
                        "-ffunction-sections",
                        "-fdata-sections",
                        "-fno-unwind-tables",
                        "-fno-asynchronous-unwind-tables",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                        "-fno-ident",
                        "-c",
                        str(SOURCE),
                        "-o",
                        str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwinit.o")),
                    ],
                    check=True,
                    capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
