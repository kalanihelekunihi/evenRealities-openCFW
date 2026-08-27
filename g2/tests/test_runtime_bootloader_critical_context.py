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
FIXTURE = ROOT / "tests/fixtures/bootloader_critical_context_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_critical_context.c"


class BootloaderCriticalContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-critical-context.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_critical_context_set.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
        ]
        cls.lib.open_cfw_bootloader_critical_context.restype = ctypes.c_uint
        cls.lib.open_cfw_test_critical_context_runtime_calls.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, values: tuple[int, int, int, int]) -> tuple[int, int]:
        self.lib.open_cfw_test_critical_context_set(*values)
        return (
            self.lib.open_cfw_bootloader_critical_context(),
            self.lib.open_cfw_test_critical_context_runtime_calls(),
        )

    def test_authenticated_complete_stock_entry(self) -> None:
        body = OFFICIAL.read_bytes()[0x602A:0x6058]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            46,
            "e9208bab7b82a1d6f0228d69b2707c5cfadd5cb45b7d24963defe8cabb00b32b",
        ))

    def test_interrupt_and_mask_contract(self) -> None:
        self.assertEqual(self.run_case((7, 0, 0, 0)), (1, 0))
        self.assertEqual(self.run_case((0, 1, 1, 1)), (0, 1))
        self.assertEqual(self.run_case((0, 0, 1, 0)), (1, 1))
        self.assertEqual(self.run_case((0, 2, 0, 4)), (1, 1))
        self.assertEqual(self.run_case((0, 0, 0, 0)), (0, 1))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "critical-context.o"
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
