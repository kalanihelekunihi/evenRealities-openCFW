from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_popcount_421584.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_popcount_host.c"


class BootloaderPopcountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "popcount.dylib" if sys.platform == "darwin" else "popcount.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.popcount = cls.lib.open_cfw_bootloader_popcount_421584
        cls.popcount.argtypes = [ctypes.c_uint32]
        cls.popcount.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_body_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x11584:0x115AE]
        self.assertEqual(len(body), 42)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "3e1aafd1c98933503de46a42099c9e0ea5b6af861f1edda36f8df25079ce834d",
        )
        self.assertEqual(blob[0x1161C:0x11620].hex(), "fff7b2ff")

    def test_population_count_contract(self) -> None:
        cases = [0, 1, 2, 3, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0x80000000]
        randomizer = random.Random(0x421584)
        cases.extend(randomizer.getrandbits(32) for _ in range(512))
        for value in cases:
            with self.subTest(value=value):
                self.assertEqual(self.popcount(value), bin(value).count("1"))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-popcount.o")
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output),
                ],
                check=True, capture_output=True,
            )
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
