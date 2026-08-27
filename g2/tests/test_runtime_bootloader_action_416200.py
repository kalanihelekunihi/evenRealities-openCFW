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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_action_416200_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_action_416200.c"


class BootloaderRuntimeAction416200Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-action.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_runtime_action_reset.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_action_416200.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_action_416200.restype = ctypes.c_int
        for name in (
            "critical_calls", "predicate_calls", "action_calls",
            "predicate_argument", "action_argument",
        ):
            getattr(cls.lib, f"open_cfw_test_{name}_get").restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def counts(self) -> tuple[int, int, int]:
        return (
            self.lib.open_cfw_test_critical_calls_get(),
            self.lib.open_cfw_test_predicate_calls_get(),
            self.lib.open_cfw_test_action_calls_get(),
        )

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x6200:0x623A]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            58,
            "e4c78725081eb02641d1918a3879468520998e6bc55183b1115b2f130a39bf28",
        ))
        self.assertEqual(image[0x1DDE8:0x1DDEC].hex(), "e8f70afa")
        self.assertEqual(image[0x1E3D6:0x1E3DA].hex(), "e7f713ff")
        self.assertEqual(image[0x1E5FE:0x1E602].hex(), "e7f7fffd")

    def test_critical_and_null_short_circuits(self) -> None:
        self.lib.open_cfw_test_runtime_action_reset(1, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_action_416200(1), -6)
        self.assertEqual(self.counts(), (1, 0, 0))

        self.lib.open_cfw_test_runtime_action_reset(0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_runtime_action_416200(0), -4)
        self.assertEqual(self.counts(), (1, 0, 0))

    def test_low_byte_four_blocks_action(self) -> None:
        for predicate in (4, 0x104, 0xFFFFFF04):
            with self.subTest(predicate=predicate):
                self.lib.open_cfw_test_runtime_action_reset(0, predicate)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_action_416200(0xABCDEF01),
                    -3,
                )
                self.assertEqual(self.counts(), (1, 1, 0))
                self.assertEqual(
                    self.lib.open_cfw_test_predicate_argument_get(), 0xABCDEF01,
                )

    def test_non_four_low_byte_calls_action_once(self) -> None:
        for argument, predicate in ((1, 0), (0x12345678, 3), (0xFFFFFFFF, 0x100)):
            with self.subTest(argument=argument, predicate=predicate):
                self.lib.open_cfw_test_runtime_action_reset(0, predicate)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_action_416200(argument), 0,
                )
                self.assertEqual(self.counts(), (1, 1, 1))
                self.assertEqual(self.lib.open_cfw_test_predicate_argument_get(), argument)
                self.assertEqual(self.lib.open_cfw_test_action_argument_get(), argument)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-action.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    unittest.main()
