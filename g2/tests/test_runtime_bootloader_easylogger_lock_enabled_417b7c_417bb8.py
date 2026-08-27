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
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_easylogger_lock_enabled_417b7c.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_easylogger_lock_enabled_host.c"
STOCK_START = 0x00417B7C
STOCK_END = 0x00417BB8
STOCK_SHA256 = "61ab2f07f409287f6b8773559ad3223a72a9550cd9fc25dadfc7cb3a9ddc1c32"
CALLERS = (0x00417366,)


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - 0x00410000
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderEasyloggerLockEnabledTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "lock_enabled.dylib" if sys.platform == "darwin" else "lock_enabled.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_body_and_direct_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[STOCK_START - 0x00410000:STOCK_END - 0x00410000]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (60, STOCK_SHA256))
        callers = tuple(
            address
            for address in range(0x00410000, 0x00410000 + len(image) - 3, 2)
            if decode_bl(image, address) == STOCK_START
        )
        self.assertEqual(callers, CALLERS)

    def test_all_lock_state_transitions(self) -> None:
        for name in (
            "disabled_is_side_effect_free",
            "relocks",
            "reunlocks",
            "matching_state_is_noop",
        ):
            with self.subTest(case=name):
                function = getattr(self.loaded, f"open_cfw_test_easylogger_lock_enabled_{name}")
                function.restype = ctypes.c_uint32
                self.assertEqual(function(), 1)

    def test_source_constants_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in ("0x0041A69BU", "0x0041A6A3U", "output_is_locked_before_enable", "output_is_locked_before_disable"):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "lock_enabled.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra", "-Werror",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE=OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
