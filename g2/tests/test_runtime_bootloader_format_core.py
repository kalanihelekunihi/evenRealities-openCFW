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
FIXTURE = ROOT / "tests/fixtures/log_format_core_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_format_core.c"


class BootloaderFormatCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-format.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-DOPEN_CFW_TEST_BOOTLOADER_FORMAT_CORE",
            str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_log_core_reset.argtypes = []
        cls.lib.open_cfw_test_log_core_push_u32.argtypes = [ctypes.c_uint]
        cls.lib.open_cfw_test_log_core_push_u64.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_test_log_core_push_pointer.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_test_log_core_push_double.argtypes = [ctypes.c_double]
        cls.lib.open_cfw_test_log_core_run.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        cls.lib.open_cfw_test_log_core_run.restype = ctypes.c_uint
        cls.lib.open_cfw_test_log_core_argument_error.restype = ctypes.c_uint
        cls.lib.open_cfw_test_log_core_argument_index.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset(self) -> None:
        self.lib.open_cfw_test_log_core_reset()

    def execute(self, format_text: bytes, output: bool = True) -> tuple[int, bytes | None]:
        buffer = ctypes.create_string_buffer(1024)
        result = self.lib.open_cfw_test_log_core_run(
            ctypes.addressof(buffer) if output else None,
            format_text,
        )
        self.assertEqual(self.lib.open_cfw_test_log_core_argument_error(), 0)
        return result, buffer.value if output else None

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.lib, name)

    def test_authenticated_stock_body_and_bootloader_binding(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x5BF6:0x5FAE]
        self.assertEqual(len(body), 952)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "43f3f8c080c595922a87cf7657943dcea958b983e5f3a78a244d513f42b232bb",
        )
        self.assertEqual(int.from_bytes(blob[0x5FE0:0x5FE4], "little"), 0x200271C4)
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("0x200271C4U", source)
        self.assertIn("open_cfw_bootloader_float_to_fixed", source)
        self.assertIn("log_format_core.c", source)

    def test_literals_crlf_strings_and_null_output(self) -> None:
        self.reset()
        self.assertEqual(self.execute(b"plain %% %q"), (9, b"plain % q"))
        self.word("open_cfw_test_log_core_crlf_enabled").value = 1
        self.assertEqual(self.execute(b"a\nb"), (4, b"a\r\nb"))
        self.assertEqual(self.execute(b"a\nb", output=False), (3, None))

        self.reset()
        text = ctypes.create_string_buffer(b"abcdef")
        self.lib.open_cfw_test_log_core_push_u32(3)
        self.lib.open_cfw_test_log_core_push_pointer(ctypes.addressof(text))
        self.assertEqual(self.execute(b"%.*s"), (3, b"abc"))

    def test_integer_width_case_and_64_bit_contracts(self) -> None:
        self.reset()
        for value in (0xFFFFFFFF, 0x2A, 0xBEEF, (-12) & 0xFFFFFFFF):
            self.lib.open_cfw_test_log_core_push_u32(value)
        self.lib.open_cfw_test_log_core_push_u64(0xFFFFFFFF, 0xFFFFFFFF)
        result, output = self.execute(b"%u|%x|%X|%05d|%llu")
        expected = b"4294967295|2a|BEEF|-0012|18446744073709551615"
        self.assertEqual((result, output), (len(expected), expected))
        self.assertEqual(self.lib.open_cfw_test_log_core_argument_index(), 5)

    def test_float_success_fallback_and_null_output_quirk(self) -> None:
        self.reset()
        self.lib.open_cfw_test_log_core_push_double(1.25)
        self.assertEqual(self.execute(b"%f", output=False), (0, None))
        self.assertEqual(self.lib.open_cfw_test_log_core_argument_index(), 0)

        self.reset()
        self.lib.open_cfw_test_log_core_push_double(1.25)
        ctypes.c_int.in_dll(self.lib, "open_cfw_test_log_core_float_result").value = 4
        (ctypes.c_char * 32).in_dll(
            self.lib, "open_cfw_test_log_core_float_text"
        ).value = b"1.25"
        self.assertEqual(self.execute(b"%.2f"), (4, b"1.25"))
        self.assertEqual(self.word("open_cfw_test_log_core_float_capacity").value, 20)
        self.assertEqual(self.word("open_cfw_test_log_core_float_precision").value, 2)

        for error, expected in ((-1, b"0.0"), (-2, b"#.#"), (-7, b"?.?")):
            self.reset()
            self.lib.open_cfw_test_log_core_push_double(-2.5)
            ctypes.c_int.in_dll(
                self.lib, "open_cfw_test_log_core_float_result"
            ).value = error
            self.assertEqual(self.execute(b"%F"), (3, expected))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "format-core.o"
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
