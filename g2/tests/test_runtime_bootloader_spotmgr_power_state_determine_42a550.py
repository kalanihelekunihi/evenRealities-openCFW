from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_determine_42a550.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
START = 0x0042A550
END = 0x0042A85E

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


class PowerStatus(ctypes.Structure):
    _fields_ = [
        ("device_power", ctypes.c_uint32),
        ("audio_power", ctypes.c_uint32),
        ("memory_power", ctypes.c_uint32),
        ("ssram_power", ctypes.c_uint32),
        ("temperature_range", ctypes.c_uint8),
        ("cpu_state", ctypes.c_uint8),
        ("gpu_state", ctypes.c_uint8),
    ]


def reference(status: PowerStatus, retained: int, collapse: int) -> tuple[int, int | None, int | None]:
    cpu = 1 if status.cpu_state == 1 else (
        0 if status.cpu_state == 0 else int((retained & 3) == 2)
    )
    shifted_device = (status.device_power << 2) & 0xFFFFFFFF
    periph = int(shifted_device != 0 or (status.audio_power & 0x4C4) != 0)
    gpu = 2 if status.gpu_state == 2 else (1 if status.gpu_state == 1 else 0)
    gpu_sdio = int(
        status.gpu_state in (1, 2) or
        (status.device_power & 0x00C00000) != 0
    )
    periph1 = int(status.gpu_state in (1, 2) or periph)
    descriptor = (
        cpu | (periph1 << 4) | ((status.temperature_range & 15) << 8) |
        (gpu << 12) | (periph << 16) | (gpu_sdio << 20)
    )
    power_map = {
        0x000300: 4 if collapse else 0,
        0x000200: 5 if collapse else 1,
        0x000100: 6 if collapse else 2,
        0x000000: 7 if collapse else 3,
        0x000310: 4, 0x000210: 5, 0x000110: 6, 0x000010: 7,
        0x000301: 12 if collapse else 8,
        0x000201: 13 if collapse else 9,
        0x000101: 14 if collapse else 10,
        0x000001: 15 if collapse else 11,
        0x000311: 12, 0x100311: 12,
        0x000211: 13, 0x100211: 13,
        0x000111: 14, 0x100111: 14,
        0x000011: 15, 0x100011: 15,
        0x100310: 16, 0x100210: 17,
        0x100110: 18, 0x100010: 19,
    }
    power = power_map.get(descriptor & 0x00F00FFF)
    if power is None:
        return 5, None, None
    ton_map = {
        0x00000: 0, 0x00001: 7 if collapse else 1,
        0x01000: 2, 0x11000: 2,
        0x02000: 3, 0x12000: 3,
        0x01001: 4, 0x11001: 4,
        0x02001: 5, 0x12001: 5,
        0x10000: 6, 0x10001: 7,
    }
    ton = ton_map.get(descriptor & 0x000FF00F)
    return (0, power, ton) if ton is not None else (5, power, None)


class BootloaderSpotmgrPowerStateDetermineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "spot-state-host.dylib"
        subprocess.run([
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
            "-Wextra", "-Werror", "-dynamiclib", str(SOURCE), "-o",
            str(cls.library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.function = getattr(
            cls.lib, "open_cfw_bootloader_spotmgr_power_state_determine_42a550"
        )
        cls.function.argtypes = [
            ctypes.POINTER(PowerStatus), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exhaustive_descriptor_classes(self) -> None:
        cases = 0
        for temperature in range(16):
            for cpu in range(4):
                for gpu in range(4):
                    for device in (0, 1, 0x00400000, 0x40000000, 0xFFFFFFFF):
                        for audio in (0, 4, 0x400, 0x80000000):
                            for retained in range(4):
                                for collapse in range(2):
                                    status = PowerStatus(
                                        device, audio, 0xAAAAAAAA, 0x55555555,
                                        temperature, cpu, gpu,
                                    )
                                    power = ctypes.c_uint32(0xDEADBEEF)
                                    ton = ctypes.c_uint32(0xBAADF00D)
                                    actual = self.function(
                                        ctypes.byref(status), ctypes.byref(power),
                                        ctypes.byref(ton), retained, collapse,
                                    )
                                    expected, expected_power, expected_ton = reference(
                                        status, retained, collapse
                                    )
                                    self.assertEqual(actual, expected)
                                    self.assertEqual(
                                        power.value,
                                        0xDEADBEEF if expected_power is None else expected_power,
                                    )
                                    self.assertEqual(
                                        ton.value,
                                        0xBAADF00D if expected_ton is None else expected_ton,
                                    )
                                    cases += 1
        self.assertEqual(cases, 40_960)

    def test_authenticated_literals_and_main_analogue(self) -> None:
        boot = BOOT.read_bytes()
        main = MAIN.read_bytes()
        literals = (
            (0x0042ACC0, 0x00434168), (0x0042ACC4, 0x40021000),
            (0x0042ACC8, 0x00F00FFF), (0x0042ACCC, 0x000FFCFF),
            (0x0042ACD0, 0x2002708C), (0x0042ACD4, 0x000FF00F),
            (0x0042ACD8, 0x00011001), (0x0042ACDC, 0x00012001),
        )
        for address, value in literals:
            self.assertEqual(
                int.from_bytes(boot[address - BOOT_BASE:address - BOOT_BASE + 4], "little"),
                value,
            )
        stock = boot[START - BOOT_BASE:END - BOOT_BASE]
        analogue = main[0x005A45D0 - MAIN_BASE:0x005A45D0 - MAIN_BASE + len(stock)]
        self.assertEqual(hashlib.sha256(analogue).hexdigest(),
                         "d0d3ba15ffab7241ceeed1292ed98b98c9ca45c57921de74bfe4142004666e91")
        self.assertEqual(sum(a == b for a, b in zip(stock, analogue)), 750)

    def test_both_reviewed_compilers_reproduce_exact_body(self) -> None:
        stock = BOOT.read_bytes()[START - BOOT_BASE:END - BOOT_BASE]
        for clang, version in (
            (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
            (Path("/opt/homebrew/opt/llvm@22/bin/clang"), "Homebrew clang version 22.1.8"),
        ):
            if not clang.exists():
                self.skipTest(f"reviewed compiler unavailable: {clang}")
            self.assertTrue(subprocess.run(
                [str(clang), "--version"], check=True, capture_output=True, text=True,
            ).stdout.startswith(version))
            output = Path(self.temporary.name) / f"{clang.parent.name}-state.o"
            subprocess.run([
                str(clang), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
                "-Werror", "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            payload, sections = apollo_overlay.parse_elf32(output)
            section = apollo_overlay.section_named(
                sections, ".text.open_cfw_bootloader_spotmgr_power_state_determine_42a550"
            )
            body = payload[int(section["offset"]):int(section["offset"]) + int(section["size"])]
            relocation_sections = [
                item for item in sections if int(item["type"]) == 9 and
                int(item["info"]) == int(section["index"])
            ]
            self.assertEqual(relocation_sections, [])
            self.assertEqual(body, stock)
            self.assertEqual(hashlib.sha256(body).hexdigest(),
                             "73e2c284f4c3efc45c0cb02ad3d2d5c520c56ce136e4c185a4fbd56b815a0d87")


if __name__ == "__main__":
    unittest.main()
