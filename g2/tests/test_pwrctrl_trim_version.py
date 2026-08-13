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
SOURCE = COMPONENT_ROOT / "pwrctrl_trim_version.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_trim_version_host.c"
)


class PwrctrlTrimVersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_trim_version.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_trim_version.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_pwrctrl_trim_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.get_trim = cls.loaded.open_cfw_pwrctrl_trim_version_get
        cls.get_trim.argtypes = [ctypes.POINTER(ctypes.c_uint)]
        cls.get_trim.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_pwrctrl_trim_{name}",
        )

    def assert_read_abi(self) -> None:
        self.assertEqual(self.word("read_calls").value, 1)
        self.assertEqual(self.word("info_space").value, 1)
        self.assertEqual(self.word("word_offset").value, 0x244)
        self.assertEqual(self.word("word_count").value, 1)
        self.assertEqual(
            self.word("destination_matches_cache").value,
            1,
        )

    def test_uninitialized_cache_reads_info1_and_returns_revision(self) -> None:
        self.word("read_value").value = 0x12345678
        output = ctypes.c_uint(0xDEADBEEF)

        result = self.get_trim(ctypes.byref(output))

        self.assertEqual(result, 0)
        self.assertEqual(output.value, 0x12345678)
        self.assertEqual(self.word("cache").value, 0x12345678)
        self.assert_read_abi()

    def test_cached_revision_skips_info1_read(self) -> None:
        self.word("cache").value = 0x89ABCDEF
        self.word("read_value").value = 0x11111111
        output = ctypes.c_uint()

        result = self.get_trim(ctypes.byref(output))

        self.assertEqual(result, 0)
        self.assertEqual(output.value, 0x89ABCDEF)
        self.assertEqual(self.word("read_calls").value, 0)

    def test_zero_or_failed_info1_read_normalizes_cache_to_zero(self) -> None:
        for read_value, status in (
            (0, 0),
            (0, 7),
            (0x12345678, 1),
            (0xFFFFFFFF, 0xFFFFFFFF),
        ):
            with self.subTest(read_value=read_value, status=status):
                self.reset_fixture()
                self.word("read_value").value = read_value
                self.word("read_status").value = status
                output = ctypes.c_uint(0xDEADBEEF)

                result = self.get_trim(ctypes.byref(output))

                self.assertEqual(result, 0)
                self.assertEqual(output.value, 0)
                self.assertEqual(self.word("cache").value, 0)
                self.assert_read_abi()

    def test_null_output_initializes_before_returning_invalid_argument(
        self,
    ) -> None:
        self.word("read_value").value = 0x76543210

        result = self.get_trim(None)

        self.assertEqual(result, 6)
        self.assertEqual(self.word("cache").value, 0x76543210)
        self.assert_read_abi()

    def test_failed_initialization_is_not_retried_after_zero_cache(self) -> None:
        self.word("read_value").value = 0x13579BDF
        self.word("read_status").value = 1
        first = ctypes.c_uint()
        second = ctypes.c_uint(0xFFFFFFFF)

        self.assertEqual(self.get_trim(ctypes.byref(first)), 0)
        self.word("read_value").value = 0x2468ACE0
        self.word("read_status").value = 0
        self.assertEqual(self.get_trim(ctypes.byref(second)), 0)

        self.assertEqual(first.value, 0)
        self.assertEqual(second.value, 0)
        self.assertEqual(self.word("cache").value, 0)
        self.assertEqual(self.word("read_calls").value, 1)

    def test_deterministic_randomized_stock_model(self) -> None:
        generator = random.Random(0x0047EF38)
        for _ in range(1000):
            self.reset_fixture()
            cache = generator.getrandbits(32)
            read_value = generator.getrandbits(32)
            read_status = generator.getrandbits(32)
            use_null = bool(generator.getrandbits(1))
            self.word("cache").value = cache
            self.word("read_value").value = read_value
            self.word("read_status").value = read_status
            output = ctypes.c_uint(generator.getrandbits(32))
            initial_output = output.value

            result = self.get_trim(
                None if use_null else ctypes.byref(output)
            )

            expected_cache = cache
            expected_calls = 0
            if cache == 0xFFFFFFFF:
                expected_calls = 1
                expected_cache = (
                    read_value
                    if read_value != 0 and read_status == 0
                    else 0
                )
            self.assertEqual(self.word("cache").value, expected_cache)
            self.assertEqual(self.word("read_calls").value, expected_calls)
            self.assertEqual(result, 6 if use_null else 0)
            self.assertEqual(
                output.value,
                initial_output if use_null else expected_cache,
            )

    def test_source_and_fixture_are_pinned(self) -> None:
        expected = {
            SOURCE: "5217470c68ee64f9d9c05c47d79c622b2510c1252a9a83468a1fffb499de51d6",
            FIXTURE: "6e96d112bccd7749e9981ecd907e6ca80a7c0238e5897db0bf2deec8dda49d8f",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
