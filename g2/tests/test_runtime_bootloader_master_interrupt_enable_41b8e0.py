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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_master_interrupt_enable_41b8e0.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_master_interrupt_enable_41b8e0_host.c"
CALLER = ROOT / "components/bootloader/core_overlay/runtime_mspi_low_level_init_420254.c"
RUN_BASE = 0x00410000
ENTRY = 0x0041B8E0
END = 0x0041B8E8


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x3FF) << 12)
        | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderMasterInterruptEnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-master-interrupt-enable.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_mie_set.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_master_interrupt_enable_41b8e0.restype = ctypes.c_uint
        cls.lib.open_cfw_test_mie_enable_calls_made.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_body_and_direct_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[ENTRY - RUN_BASE:END - RUN_BASE]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (8, "6c169e0f7b32e9f34f42114fdbd5292b812805d62399aabd65f2299c040bd120"),
        )
        callers = tuple(
            address
            for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
            if decode_bl(image, address) == ENTRY
        )
        # The sole caller is the MSPI low-level initializer's default-case
        # trampoline, which folds its literal function-pointer constant
        # 0x0041B8E1 (checked below) into this single direct BL.
        self.assertEqual(callers, (0x00420418,))

    def test_indirect_caller_literal_is_unchanged(self) -> None:
        text = CALLER.read_text(encoding="utf-8")
        self.assertIn("0x0041B8E1U", text)

    def test_returns_prior_primask_and_always_enables(self) -> None:
        for primask in (0, 1):
            with self.subTest(primask=primask):
                self.lib.open_cfw_test_mie_set(primask)
                result = self.lib.open_cfw_bootloader_master_interrupt_enable_41b8e0()
                self.assertEqual(result, primask)
                self.assertEqual(self.lib.open_cfw_test_mie_enable_calls_made(), 1)

    def test_freestanding_target_compiles_byte_identical_to_stock(self) -> None:
        output = Path(self.temporary.name) / "master-interrupt-enable.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-fno-jump-tables", "-fomit-frame-pointer",
                "-mno-unaligned-access", "-fropi",
                "-mllvm", "-enable-machine-outliner=never",
                "-Wall", "-Wextra", "-Werror", "-fno-ident",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        extracted = Path(self.temporary.name) / "master-interrupt-enable.bin"
        subprocess.run(
            [
                "/opt/homebrew/opt/llvm/bin/llvm-objcopy", "-O", "binary",
                "--only-section=.text.open_cfw_bootloader_master_interrupt_enable_41b8e0",
                str(output), str(extracted),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        body = extracted.read_bytes()
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (8, "6c169e0f7b32e9f34f42114fdbd5292b812805d62399aabd65f2299c040bd120"),
        )


if __name__ == "__main__":
    unittest.main()
