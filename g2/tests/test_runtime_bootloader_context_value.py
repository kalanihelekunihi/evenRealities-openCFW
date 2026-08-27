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
FIXTURE = ROOT / "tests/fixtures/bootloader_context_value_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_context_value.c"


class BootloaderContextValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-context-value.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_context_value_set.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_context_value.restype = ctypes.c_uint
        for name in ("context_calls", "normal_calls", "critical_calls"):
            getattr(cls.lib, f"open_cfw_test_context_value_{name}").restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, critical: int) -> tuple[int, int, int, int]:
        self.lib.open_cfw_test_context_value_set(critical, 0x11223344, 0xAABBCCDD)
        result = self.lib.open_cfw_bootloader_context_value()
        return (
            result,
            self.lib.open_cfw_test_context_value_context_calls(),
            self.lib.open_cfw_test_context_value_normal_calls(),
            self.lib.open_cfw_test_context_value_critical_calls(),
        )

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x60E8:0x60FE]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            22,
            "4fe35d35c5f61f5683c7ddd34f424d7f51d8a9276a0249c71b8473811dc7890a",
        ))
        self.assertEqual(
            [image[offset:offset + 4].hex() for offset in (0xA6AC, 0x1E382, 0x1E82C)],
            ["fbf71cfd", "e7f7b1fe", "e7f75cfc"],
        )

    def test_exact_context_dispatch(self) -> None:
        self.assertEqual(self.run_case(0), (0x11223344, 1, 1, 0))
        self.assertEqual(self.run_case(1), (0xAABBCCDD, 1, 0, 1))
        self.assertEqual(self.run_case(7), (0xAABBCCDD, 1, 0, 1))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "context-value.o"
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
