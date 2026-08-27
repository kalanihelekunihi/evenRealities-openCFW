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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_flags_wait_416590_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_flags_wait_416590.c"


class BootloaderRuntimeFlagsWait416590Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-flags-wait.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t
        cls.lib.open_cfw_test_flags_wait_reset.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_flags_wait_416590.argtypes = [word, word, word, word]
        cls.lib.open_cfw_bootloader_runtime_flags_wait_416590.restype = word
        for name in (
            "context_calls", "backend_calls", "object", "flags", "clear",
            "wait_all", "timeout",
        ):
            getattr(cls.lib, f"open_cfw_test_flags_wait_{name}").restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_caller_and_intervening_literal(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x6590:0x6610]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (128, "df03eb8655d29e3f5b6a64d2dc42f56c716c83f56f6c6689afd419f7e824d6db"),
        )
        self.assertEqual(image[0x1E2C0:0x1E2C4].hex(), "e8f766f9")
        self.assertEqual(image[0x658C:0x6590].hex(), "d4700220")

    def test_invalid_object_or_reserved_flag_byte_short_circuits(self) -> None:
        for object_value, flags in ((0, 1), (1, 0x01000000)):
            with self.subTest(object=object_value, flags=flags):
                self.lib.open_cfw_test_flags_wait_reset(0, 0)
                observed = self.lib.open_cfw_bootloader_runtime_flags_wait_416590(
                    object_value, flags, 0, 0
                )
                self.assertEqual(observed, ctypes.c_size_t(-4).value)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_context_calls(), 0)

    def test_critical_context_rejects_zero_and_nonzero_timeout_differently(self) -> None:
        for timeout, expected in ((0, -6), (1, -4), (0xFFFFFFFF, -4)):
            with self.subTest(timeout=timeout):
                self.lib.open_cfw_test_flags_wait_reset(1, 0)
                observed = self.lib.open_cfw_bootloader_runtime_flags_wait_416590(
                    1, 2, 0, timeout
                )
                self.assertEqual(observed, ctypes.c_size_t(expected).value)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_backend_calls(), 0)

    def test_option_bits_map_to_wait_all_and_inverted_clear_contract(self) -> None:
        for options, expected_clear, expected_all in (
            (0, 1, 0), (1, 1, 1), (2, 0, 0), (3, 0, 1), (0xFFFFFFFC, 1, 0),
        ):
            with self.subTest(options=options):
                self.lib.open_cfw_test_flags_wait_reset(0, 0x03)
                self.lib.open_cfw_bootloader_runtime_flags_wait_416590(
                    0x11, 0x03, options, 7
                )
                self.assertEqual(self.lib.open_cfw_test_flags_wait_backend_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_object(), 0x11)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_flags(), 0x03)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_clear(), expected_clear)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_wait_all(), expected_all)
                self.assertEqual(self.lib.open_cfw_test_flags_wait_timeout(), 7)

    def test_any_and_all_satisfaction_return_backend_bits(self) -> None:
        cases = (
            (0, 0x01, 0x03, 0x01),
            (1, 0x03, 0x03, 0x03),
            (1, 0x07, 0x03, 0x07),
        )
        for options, result, flags, expected in cases:
            with self.subTest(options=options, result=result):
                self.lib.open_cfw_test_flags_wait_reset(0, result)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_flags_wait_416590(
                        1, flags, options, 5
                    ),
                    expected,
                )

    def test_unsatisfied_wait_maps_timeout_and_poll_failures(self) -> None:
        for options, result, timeout, expected in (
            (0, 0, 0, -3),
            (0, 0, 1, -2),
            (1, 1, 0, -3),
            (1, 1, 9, -2),
        ):
            with self.subTest(options=options, result=result, timeout=timeout):
                self.lib.open_cfw_test_flags_wait_reset(0, result)
                observed = self.lib.open_cfw_bootloader_runtime_flags_wait_416590(
                    1, 3, options, timeout
                )
                self.assertEqual(observed, ctypes.c_size_t(expected).value)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-flags-wait.o"
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
