from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCES = tuple(COMPONENT / name for name in ("runtime_udec_digits.c", "runtime_sdec_digits.c", "runtime_hex_digits.c", "runtime_parse_dec.c", "runtime_u64_to_dec.c", "runtime_u64_to_hex.c", "runtime_nullable_strlen.c", "runtime_repeat_char.c", "runtime_float_to_fixed.c"))
FIXTURE = ROOT / "tests/fixtures/bootloader_numeric_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderNumericTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "numeric.dylib"
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_bootloader_udec_digits_fixture.argtypes = [ctypes.c_uint64]
        cls.lib.open_cfw_bootloader_udec_digits_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_sdec_digits_fixture.argtypes = [ctypes.c_int64]
        cls.lib.open_cfw_bootloader_sdec_digits_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_hex_digits_fixture.argtypes = [ctypes.c_uint64]
        cls.lib.open_cfw_bootloader_hex_digits_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_parse_dec_fixture.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_bootloader_parse_dec_fixture.restype = ctypes.c_int32
        cls.lib.open_cfw_bootloader_u64_to_dec_fixture.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_char)]
        cls.lib.open_cfw_bootloader_u64_to_dec_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_u64_to_hex_fixture.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_char), ctypes.c_uint32]
        cls.lib.open_cfw_bootloader_u64_to_hex_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_nullable_strlen_fixture.argtypes = [ctypes.c_char_p]
        cls.lib.open_cfw_bootloader_nullable_strlen_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_repeat_char_fixture.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_uint32, ctypes.c_int32]
        cls.lib.open_cfw_bootloader_repeat_char_fixture.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_float_to_fixed_fixture.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int32, ctypes.c_float]
        cls.lib.open_cfw_bootloader_float_to_fixed_fixture.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_digit_counts(self) -> None:
        unsigned = (0, 1, 9, 10, 99, 100, (1 << 64) - 1)
        for value in unsigned:
            self.assertEqual(self.lib.open_cfw_bootloader_udec_digits_fixture(value), len(str(value)))
            self.assertEqual(self.lib.open_cfw_bootloader_hex_digits_fixture(value), len(format(value, "x")))
        signed = (0, 1, -1, 10, -10, (1 << 63) - 1, -(1 << 63))
        for value in signed:
            self.assertEqual(self.lib.open_cfw_bootloader_sdec_digits_fixture(value), len(str(abs(value))))

    def test_parse_decimal_contract(self) -> None:
        cases = ((b"", 0, 0), (b"-", 0, 1), (b"123x", 123, 3), (b"-42!", -42, 3), (b"+7", 0, 0), (b"4294967296z", 0, 10))
        for text, expected, expected_count in cases:
            count = ctypes.c_uint32(0xFFFFFFFF)
            self.assertEqual(self.lib.open_cfw_bootloader_parse_dec_fixture(text, ctypes.byref(count)), expected)
            self.assertEqual(count.value, expected_count)
        self.assertEqual(self.lib.open_cfw_bootloader_parse_dec_fixture(b"7", None), 7)

    def test_unsigned_decimal_output_contract(self) -> None:
        for value in (0, 1, 9, 10, 99, 100, (1 << 32) - 1, 1 << 63, (1 << 64) - 1):
            output = ctypes.create_string_buffer(21)
            expected = str(value).encode("ascii")
            self.assertEqual(self.lib.open_cfw_bootloader_u64_to_dec_fixture(value, output), len(expected))
            self.assertEqual(output.value, expected)
            self.assertEqual(self.lib.open_cfw_bootloader_u64_to_dec_fixture(value, None), len(expected))

    def test_unsigned_hex_output_contract(self) -> None:
        for value in (0, 1, 15, 16, 255, (1 << 32) - 1, 1 << 63, (1 << 64) - 1):
            for lowercase, specifier in ((0, "X"), (1, "x"), (0x100, "x")):
                output = ctypes.create_string_buffer(17)
                expected = format(value, specifier).encode("ascii")
                self.assertEqual(self.lib.open_cfw_bootloader_u64_to_hex_fixture(value, output, lowercase), len(expected))
                self.assertEqual(output.value, expected)
                self.assertEqual(self.lib.open_cfw_bootloader_u64_to_hex_fixture(value, None, lowercase), len(expected))

    def test_nullable_strlen_and_repeat_contracts(self) -> None:
        self.assertEqual(self.lib.open_cfw_bootloader_nullable_strlen_fixture(None), 0)
        for text in (b"", b"a", b"embedded spaces", b"1234567890"):
            self.assertEqual(self.lib.open_cfw_bootloader_nullable_strlen_fixture(text), len(text))
        for count in (-2, -1, 0, 1, 7):
            output = ctypes.create_string_buffer(8)
            expected_count = max(count, 0)
            self.assertEqual(self.lib.open_cfw_bootloader_repeat_char_fixture(output, ord("Z"), count), expected_count)
            self.assertEqual(output.raw[:expected_count], b"Z" * expected_count)
            self.assertEqual(self.lib.open_cfw_bootloader_repeat_char_fixture(None, ord("Z"), count), expected_count)

    def test_fixed_float_contract(self) -> None:
        cases = ((0.0, 6, b"0.0"), (-0.0, 6, b"0.0"), (1.5, 3, b"1.500"), (-2.25, 2, b"-2.25"), (1.999, 2, b"2.00"), (0.125, 3, b"0.125"), (12.0, 6, b"12.0"))
        for value, precision, expected in cases:
            output = ctypes.create_string_buffer(32)
            ctypes.c_uint32.from_buffer(output).value = 20
            result = self.lib.open_cfw_bootloader_float_to_fixed_fixture(output, precision, value)
            self.assertEqual(result, len(expected))
            self.assertEqual(output.value, expected)

        output = ctypes.create_string_buffer(32)
        ctypes.c_uint32.from_buffer(output).value = 3
        self.assertEqual(self.lib.open_cfw_bootloader_float_to_fixed_fixture(output, 2, 1.0), -3)
        for value, expected_error in ((2.0 ** -24, -1), (2.0 ** 31, -2), (float("inf"), -2), (float("nan"), -2)):
            ctypes.c_uint32.from_buffer(output).value = 20
            self.assertEqual(self.lib.open_cfw_bootloader_float_to_fixed_fixture(output, 2, value), expected_error)

    def test_authenticated_stock_entries(self) -> None:
        blob = OFFICIAL.read_bytes()
        expected = ((0x5900, 0x5924, "5cb5a2122755c72fe1feee92066675fd744718498be799c4b7163476c5bb30da"), (0x5924, 0x5936, "84075552582aa3faed79585d7af9bfad49ea10cf6c5f023343cf1acd47ae5b35"), (0x5936, 0x595C, "b32fcab992f19ef52dc494a38c6c8a5269c8bb5ec39f0a62ddb3030ef01280d7"), (0x595C, 0x59A0, "82f777f8f00d318187e88d72d7a0a4d5d7a61b8ea7e1981b9d3472999e433caf"), (0x59A0, 0x5A08, "8d34c568f2d0799b69f812076b3c2a84f2ee6c9c5a0e46a2782e87f9c2a435e0"), (0x5A08, 0x5A7C, "e53ad1ebe639d9b80c3bf2f5a2c2228698a5a0b9849cc0ddebdea54e7caee28c"), (0x5A7C, 0x5A94, "b2232233b8706cc7900d6aea4f778cc04d1859ba9a969ea895a2648eecb364d1"), (0x5A94, 0x5AB6, "e8b9ffb732e3d15c42a4e890c903fa548091b27e57858fa91044b78ff127b636"), (0x5AB6, 0x5BF6, "d3c06c2907e1a0e8b3890aae57449889724a45e0a45bb167c8947d8de11743d6"))
        for start, end, digest in expected:
            body = blob[start:end]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_freestanding_sources_compile(self) -> None:
        for source in SOURCES:
            output = Path(self.temporary.name) / f"{source.stem}.o"
            subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-mllvm", "-enable-machine-outliner=never", "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(output)], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
