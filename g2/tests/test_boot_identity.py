from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "boot_identity.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "boot_identity_host.c"
UINT_MASK = (1 << 32) - 1


class BootIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "boot_identity.dylib"
            if sys.platform == "darwin"
            else "boot_identity.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset_status = cls.loaded.open_cfw_reset_status_word
        cls.reset_status.argtypes = []
        cls.reset_status.restype = ctypes.c_int
        cls.version_code = cls.loaded.open_cfw_firmware_version_code
        cls.version_code.argtypes = []
        cls.version_code.restype = ctypes.c_uint
        cls.trace = (
            ctypes.c_uint * 4
        ).in_dll(cls.loaded, "open_cfw_test_boot_identity_trace")
        cls.version = (
            ctypes.c_char * 128
        ).in_dll(cls.loaded, "open_cfw_test_boot_identity_version")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    def reset_status_fixture(self, *, status: int, result: int = 0) -> None:
        self.word("open_cfw_test_boot_identity_status_word").value = (
            status & UINT_MASK
        )
        self.word("open_cfw_test_boot_identity_status_result").value = (
            result & UINT_MASK
        )
        for name in (
            "open_cfw_test_boot_identity_clear_calls",
            "open_cfw_test_boot_identity_clear_length",
            "open_cfw_test_boot_identity_status_calls",
            "open_cfw_test_boot_identity_observed_nonzero",
            "open_cfw_test_boot_identity_trace_count",
        ):
            self.word(name).value = 0
        self.trace[:] = [0] * 4

    def set_version(self, value: str) -> None:
        encoded = value.encode("ascii")
        self.assertLess(len(encoded), len(self.version))
        self.version[:] = b"\0" * len(self.version)
        self.version[:len(encoded)] = encoded

    @staticmethod
    def version_model(value: str) -> int:
        components = [0, 0, 0]
        cursor = 0
        count = 0
        while cursor < len(value) and count < 3:
            if "0" <= value[cursor] <= "9":
                parsed = 0
                while cursor < len(value) and "0" <= value[cursor] <= "9":
                    parsed = (
                        parsed * 10 + ord(value[cursor]) - ord("0")
                    ) & UINT_MASK
                    cursor += 1
                components[count] = parsed
                count += 1
            else:
                cursor += 1
        return (
            (components[0] << 16)
            | (components[1] << 8)
            | components[2]
        ) & UINT_MASK

    def test_reset_status_is_cleared_filled_and_sign_extended(self) -> None:
        cases = (
            (0x0000, 0),
            (0x7FFF, 32767),
            (0x8000, -32768),
            (0xFFFF, -1),
            (0x12345678, 0x5678),
        )
        for status, expected in cases:
            with self.subTest(status=status):
                self.reset_status_fixture(status=status, result=0xDEADBEEF)
                self.assertEqual(self.reset_status(), expected)
                self.assertEqual(
                    self.word(
                        "open_cfw_test_boot_identity_clear_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_boot_identity_clear_length"
                    ).value,
                    16,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_boot_identity_status_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_boot_identity_observed_nonzero"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.trace[
                        :self.word(
                            "open_cfw_test_boot_identity_trace_count"
                        ).value
                    ],
                    [1, 2],
                )

    def test_reset_status_ignores_provider_result(self) -> None:
        for result in (0, 1, 6, UINT_MASK):
            with self.subTest(result=result):
                self.reset_status_fixture(status=0xA55A, result=result)
                self.assertEqual(self.reset_status(), -23206)

    def test_randomized_reset_status_model(self) -> None:
        generator = random.Random(0x0047DCEC)
        for _ in range(500):
            status = generator.getrandbits(32)
            self.reset_status_fixture(
                status=status,
                result=generator.getrandbits(32),
            )
            low = status & 0xFFFF
            expected = low if low < 0x8000 else low - 0x10000
            self.assertEqual(self.reset_status(), expected)

    def test_stock_version_and_separator_variants(self) -> None:
        for value in (
            "2.2.6.10",
            "v2-2_6+10",
            "2",
            "2.2",
            "2.2.6.10.99",
            "abc",
            "",
            "001.002.006",
        ):
            with self.subTest(value=value):
                self.set_version(value)
                self.assertEqual(
                    self.version_code(),
                    self.version_model(value),
                )
        self.set_version("2.2.6.10")
        self.assertEqual(self.version_code(), 0x00020206)

    def test_randomized_version_parser_model(self) -> None:
        generator = random.Random(0x0047DD08)
        alphabet = "0123456789.-_vabc"
        for _ in range(500):
            value = "".join(
                generator.choice(alphabet)
                for _ in range(generator.randrange(0, 80))
            )
            self.set_version(value)
            self.assertEqual(
                self.version_code(),
                self.version_model(value),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c61ddd0a30dfac196f7147ffb054c29ebbb66637d9de9e57d5466c4979886f7c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "edf4e44114ea595c8051aa6d54db945d0520720ef960e9dd8e03a00257c780ea",
        )


if __name__ == "__main__":
    unittest.main()
