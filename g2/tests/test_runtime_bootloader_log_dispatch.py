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
FIXTURE = ROOT / "tests/fixtures/bootloader_log_dispatch_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_log_dispatch.c"


class BootloaderLogDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-log-dispatch.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_log_dispatch_reset.argtypes = []
        cls.lib.open_cfw_test_log_dispatch_enable.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_log_dispatch_set_result.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_log_dispatch_run.argtypes = [ctypes.c_char_p]
        cls.lib.open_cfw_test_log_dispatch_run.restype = ctypes.c_uint
        for name in (
            "open_cfw_test_log_dispatch_format_calls",
            "open_cfw_test_log_dispatch_handler_one_calls",
            "open_cfw_test_log_dispatch_handler_two_calls",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint
        for name in (
            "open_cfw_test_log_dispatch_seen_cursor",
            "open_cfw_test_log_dispatch_seen_context",
            "open_cfw_test_log_dispatch_context",
        ):
            getattr(cls.lib, name).restype = ctypes.c_void_p
        cls.lib.open_cfw_test_log_dispatch_seen_format.restype = ctypes.c_char_p
        cls.lib.open_cfw_test_log_dispatch_output.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_log_dispatch_reset()

    def test_authenticated_stock_body_and_fixed_sram_bindings(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x5FAE:0x5FDA]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            44,
            "4dd35a80dd88663be85e71c3b7e3bf5409c1e4e2150ec3fd1d66133b6d2ad0ea",
        ))
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("0x200270CCU", source)
        self.assertIn("0x20024CD0U", source)

    def test_null_handler_short_circuits_without_formatting(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_run(b"ignored"), 0)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_format_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_handler_one_calls(), 0)

    def test_enabled_handler_formats_dispatches_and_returns_count(self) -> None:
        self.lib.open_cfw_test_log_dispatch_enable(0)
        self.lib.open_cfw_test_log_dispatch_set_result(37)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_run(b"value=%u"), 37)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_format_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_handler_one_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_handler_two_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_seen_format(), b"value=%u")
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_seen_cursor(), 0x12345678)
        self.assertEqual(
            self.lib.open_cfw_test_log_dispatch_seen_context(),
            self.lib.open_cfw_test_log_dispatch_context(),
        )
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_output(), b"formatted")

    def test_handler_is_reloaded_after_formatter_returns(self) -> None:
        self.lib.open_cfw_test_log_dispatch_enable(1)
        self.lib.open_cfw_test_log_dispatch_set_result(9)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_run(b"switch"), 9)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_handler_one_calls(), 0)
        self.assertEqual(self.lib.open_cfw_test_log_dispatch_handler_two_calls(), 1)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "log-dispatch.o"
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
