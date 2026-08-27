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
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_call_4161ce_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_call_4161ce.c"


class BootloaderRuntimeCall4161ceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-call.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_runtime_call_reset.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_bootloader_runtime_call_4161ce.argtypes = [
            ctypes.c_uint, ctypes.c_uint,
        ]
        cls.lib.open_cfw_bootloader_runtime_call_4161ce.restype = ctypes.c_int
        cls.lib.open_cfw_test_critical_context_calls_get.restype = ctypes.c_uint
        cls.lib.open_cfw_test_retained_calls_get.restype = ctypes.c_uint
        cls.lib.open_cfw_test_retained_argument_0_get.restype = ctypes.c_uint
        cls.lib.open_cfw_test_retained_argument_1_get.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x61CE:0x6200]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            50,
            "e57752e75553f8e047c24eefdd649e5d9f1b2941234488ec1868197557986a55",
        ))
        self.assertEqual(image[0x1E28C:0x1E290].hex(), "e7f79fff")
        self.assertEqual(image[0x1E29C:0x1E2A0].hex(), "e7f797ff")

    def test_critical_context_fails_closed_before_argument_validation(self) -> None:
        for argument_0, argument_1 in ((0, 0), (1, 1), (0xFFFFFFFF, 56)):
            with self.subTest(argument_0=argument_0, argument_1=argument_1):
                self.lib.open_cfw_test_runtime_call_reset(1)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_call_4161ce(
                        argument_0, argument_1,
                    ),
                    -6,
                )
                self.assertEqual(self.lib.open_cfw_test_critical_context_calls_get(), 1)
                self.assertEqual(self.lib.open_cfw_test_retained_calls_get(), 0)

    def test_invalid_arguments_fail_without_retained_call(self) -> None:
        for argument_0, argument_1 in (
            (0, 1), (0, 56), (1, 0), (1, 57), (1, 0xFFFFFFFF),
        ):
            with self.subTest(argument_0=argument_0, argument_1=argument_1):
                self.lib.open_cfw_test_runtime_call_reset(0)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_call_4161ce(
                        argument_0, argument_1,
                    ),
                    -4,
                )
                self.assertEqual(self.lib.open_cfw_test_critical_context_calls_get(), 1)
                self.assertEqual(self.lib.open_cfw_test_retained_calls_get(), 0)

    def test_valid_selector_boundaries_forward_exact_arguments(self) -> None:
        for argument_0, argument_1 in (
            (1, 1), (0x12345678, 2), (0xFFFFFFFF, 56),
        ):
            with self.subTest(argument_0=argument_0, argument_1=argument_1):
                self.lib.open_cfw_test_runtime_call_reset(0)
                self.assertEqual(
                    self.lib.open_cfw_bootloader_runtime_call_4161ce(
                        argument_0, argument_1,
                    ),
                    0,
                )
                self.assertEqual(self.lib.open_cfw_test_critical_context_calls_get(), 1)
                self.assertEqual(self.lib.open_cfw_test_retained_calls_get(), 1)
                self.assertEqual(
                    self.lib.open_cfw_test_retained_argument_0_get(), argument_0,
                )
                self.assertEqual(
                    self.lib.open_cfw_test_retained_argument_1_get(), argument_1,
                )

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-call.o"
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
