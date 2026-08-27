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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_easylogger_output_4176ce.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_easylogger_output_host.c"
SOURCE_IDENTITY = (
    30999,
    "60859f54b54e14e4a22c180d61ea76bd63b358d6896c4787d2d0f7d40816a500",
)
STOCK = (
    0x76CE,
    0x7AD0,
    "97645514643e4e4e3e5e04a8d14a08c5c714df3cfd64e764b7b73ab95860e021",
)
CALLER_DIGEST = "47456628984211dc924d9cd6fa0c011711b7195537c8e3f0729a2894cdbed481"


class BootloaderEasyloggerOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "easylogger_output.dylib" if sys.platform == "darwin"
            else "easylogger_output.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.cases = {}
        for name in (
            "interrupt_gate", "plain_and_filters", "full_format",
            "directory_process", "keyword", "truncation",
        ):
            function = getattr(
                cls.lib, f"open_cfw_test_easylogger_output_{name}"
            )
            function.restype = ctypes.c_uint
            cls.cases[name] = function

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_authenticated_stock_body_and_all_direct_callers(self):
        sys.path.insert(0, str(ROOT / "tools"))
        try:
            from apollo_overlay import BuildError, decode_thumb_branch
        finally:
            sys.path.pop(0)

        image = OFFICIAL.read_bytes()
        start, end, expected_hash = STOCK
        body = image[start:end]
        self.assertEqual(len(body), 1026)
        self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
        callers = []
        for offset in range(0, len(image) - 3, 2):
            try:
                target = decode_thumb_branch(
                    0x00410000 + offset,
                    image[offset:offset + 4],
                    link=True,
                )
            except BuildError:
                continue
            if target == 0x004176CE:
                callers.append(0x00410000 + offset)
        encoded = ",".join(f"{address:08X}" for address in callers).encode()
        self.assertEqual(len(callers), 115)
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), CALLER_DIGEST)

    def test_interrupt_context_returns_before_arguments_or_assertion(self):
        self.assertEqual(self.cases["interrupt_gate"](), 1)

    def test_output_enable_level_tag_and_tag_level_filters(self):
        self.assertEqual(self.cases["plain_and_filters"](), 1)

    def test_color_level_tag_time_thread_function_and_line_format(self):
        self.assertEqual(self.cases["full_format"](), 1)

    def test_directory_process_and_field_delimiters(self):
        self.assertEqual(self.cases["directory_process"](), 1)

    def test_post_format_keyword_filter_unlocks_on_both_paths(self):
        self.assertEqual(self.cases["keyword"](), 1)

    def test_buffer_overflow_reserves_csi_end_and_newline_capacity(self):
        self.assertEqual(self.cases["truncation"](), 1)

    def test_source_identity_constants_and_freestanding_target_compile(self):
        source = SOURCE.read_bytes()
        self.assertEqual(
            (len(source), hashlib.sha256(source).hexdigest()), SOURCE_IDENTITY
        )
        text = source.decode()
        for token in (
            "0x20026700U", "0x200258D0U", "0x2000031CU",
            "0x20000334U", "0x200270E4U", "0x0041A693U",
            "0x0041A6ABU", "0x0041A6F1U", "0x0041A6F9U",
            "0x0041B219U", "0x0041B25DU", "572U",
            '"mrs %0, ipsr"',
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "easylogger_output.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fropi",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-mllvm", "-enable-machine-outliner=never",
                "-Wall", "-Wextra", "-Werror",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE=OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
