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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_value_4161c6_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_value_4161c6.c"


class BootloaderRuntimeValue4161c6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-value.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_runtime_value_set.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_value_4161c6.restype = ctypes.c_uint
        cls.lib.open_cfw_test_runtime_value_calls_get.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x61C6:0x61CE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            8,
            "8bca4189bfd5992611480a59010d921df4ced8b191396b455f3223c270f19f66",
        ))
        self.assertEqual(image[0x1E286:0x1E28A].hex(), "e7f79eff")
        self.assertEqual(image[0x1E296:0x1E29A].hex(), "e7f796ff")

    def test_exact_value_forwarding(self) -> None:
        for value in (0, 1, 0x12345678, 0xFFFFFFFF):
            with self.subTest(value=value):
                self.lib.open_cfw_test_runtime_value_set(value)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_value_4161c6(), value,
                )
                self.assertEqual(
                    self.lib.open_cfw_test_runtime_value_calls_get(), 1,
                )

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-value.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
