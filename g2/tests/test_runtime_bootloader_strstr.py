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
FIXTURE = ROOT / "tests/fixtures/bootloader_strstr_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_strstr.c"


class BootloaderStrstrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-strstr.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_bootloader_strstr.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls.lib.open_cfw_bootloader_strstr.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def offset(self, haystack: bytes, needle: bytes) -> int | None:
        buffer = ctypes.create_string_buffer(haystack)
        result = self.lib.open_cfw_bootloader_strstr(buffer, needle)
        return None if result is None else result - ctypes.addressof(buffer)

    def test_authenticated_complete_stock_entry(self) -> None:
        body = OFFICIAL.read_bytes()[0x5FFA:0x6026]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            44,
            "b3d23ab7bd57fe606d7b10914614adcf04fdb10bca25899ee7cd301d38f3ae40",
        ))

    def test_standard_substring_contract(self) -> None:
        cases = (
            (b"", b"", 0),
            (b"abc", b"", 0),
            (b"abc", b"a", 0),
            (b"abcabc", b"cab", 2),
            (b"aaaab", b"aaab", 1),
            (b"abc", b"c", 2),
            (b"abc", b"d", None),
            (b"short", b"shorter", None),
        )
        for haystack, needle, expected in cases:
            with self.subTest(haystack=haystack, needle=needle):
                self.assertEqual(self.offset(haystack, needle), expected)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "strstr.o"
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
