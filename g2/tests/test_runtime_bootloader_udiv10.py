from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import random
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_udiv10.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_udiv10.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_udiv10_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderUdiv10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "udiv10.dylib"
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.function = ctypes.CDLL(str(cls.library)).open_cfw_bootloader_udiv10_fixture
        cls.function.argtypes = [ctypes.c_uint64]
        cls.function.restype = ctypes.c_uint64

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_boundaries_and_deterministic_random_values(self) -> None:
        values = [0, 1, 9, 10, 11, 19, 20, 99, 100, (1 << 32) - 1, 1 << 32, (1 << 63) - 1, 1 << 63, (1 << 64) - 1]
        generator = random.Random(0x415844)
        values.extend(generator.getrandbits(64) for _ in range(1000))
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(self.function(value), value // 10)

    def test_authenticated_stock_entry(self) -> None:
        entry = OFFICIAL.read_bytes()[0x5844:0x5900]
        self.assertEqual((len(entry), hashlib.sha256(entry).hexdigest()), (188, "193eb3cd689460ea3fcc0e840a7899200f5d430b601bc86b96fe36110031a536"))

    def test_freestanding_target_compiles_without_runtime_calls(self) -> None:
        output = Path(self.temporary.name) / "udiv10-arm.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-mllvm", "-enable-machine-outliner=never", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)
        readobj = subprocess.run(["/opt/homebrew/opt/llvm/bin/llvm-readobj", "--relocations", str(output)], check=True, capture_output=True, text=True).stdout
        self.assertNotIn("R_ARM_THM_CALL", readobj)
        self.assertIn("open_cfw_bootloader_udiv10", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
