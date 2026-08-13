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
SOURCE = COMPONENT_ROOT / "pwrctrl_cpdlp_config.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_cpdlp_config_host.c"
)

CACHE_CONTROL = 0xE000ED14
CPDLP_STATE = 0xE001E300
UINT_MASK = 0xFFFFFFFF


def model(configuration: int) -> int:
    configuration &= UINT_MASK
    rlp = configuration & 0xFF
    elp = (configuration >> 8) & 0xFF
    clp = (configuration >> 16) & 0xFF
    return ((rlp << 8) | (elp << 4) | clp) & UINT_MASK


class PwrctrlCpdlpConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_cpdlp_config.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_cpdlp_config.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_cpdlp_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.configure = cls.loaded.open_cfw_pwrctrl_cpdlp_config
        cls.configure.argtypes = [ctypes.c_uint]
        cls.configure.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_cpdlp_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 2).in_dll(
            cls.loaded,
            f"open_cfw_test_cpdlp_{name}",
        )

    def run_case(
        self,
        configuration: int,
        cache_control: int = 0,
        state: int = 0xDEADBEEF,
    ) -> int:
        self.reset_fixture(cache_control, state)
        return self.configure(configuration)

    def test_cache_disabled_accepts_rlp_off_and_packs_three_bytes(
        self,
    ) -> None:
        configuration = 0x00020103

        self.assertEqual(self.run_case(configuration), 0)
        self.assertEqual(self.word("state").value, model(configuration))
        self.assertEqual(self.word("write_value").value, 0x312)

    def test_either_cache_enable_bit_rejects_rlp_off_without_write(
        self,
    ) -> None:
        for cache_control in (0x00010000, 0x00020000, 0x00030000):
            with self.subTest(cache_control=cache_control):
                self.assertEqual(
                    self.run_case(0x00A5A503, cache_control),
                    1,
                )
                self.assertEqual(self.word("state").value, 0xDEADBEEF)
                self.assertEqual(self.word("write_count").value, 0)
                self.assertEqual(list(self.words("operations")), [1, 0])

    def test_cache_enabled_accepts_all_other_rlp_values(self) -> None:
        for rlp in (0, 1, 2, 4, 0xFF):
            with self.subTest(rlp=rlp):
                configuration = 0x00020100 | rlp
                self.assertEqual(
                    self.run_case(configuration, 0x00030000),
                    0,
                )
                self.assertEqual(
                    self.word("state").value,
                    model(configuration),
                )

    def test_only_low_three_input_bytes_contribute(self) -> None:
        base = 0x00030201

        self.assertEqual(self.run_case(base), 0)
        expected = self.word("state").value
        self.assertEqual(self.run_case(base | 0xFF000000), 0)
        self.assertEqual(self.word("state").value, expected)

    def test_randomized_packed_model_and_cache_gate(self) -> None:
        generator = random.Random(0x0047FFC4)

        for _ in range(1000):
            configuration = generator.getrandbits(32)
            cache_control = generator.getrandbits(32)
            expected_failure = (
                cache_control & 0x00030000
            ) != 0 and (configuration & 0xFF) == 3

            self.assertEqual(
                self.run_case(configuration, cache_control),
                1 if expected_failure else 0,
            )
            self.assertEqual(self.word("read_count").value, 1)
            self.assertEqual(self.word("read_address").value, CACHE_CONTROL)
            if expected_failure:
                self.assertEqual(self.word("write_count").value, 0)
                self.assertEqual(self.word("state").value, 0xDEADBEEF)
            else:
                self.assertEqual(self.word("write_count").value, 1)
                self.assertEqual(self.word("write_address").value, CPDLP_STATE)
                self.assertEqual(
                    self.word("write_value").value,
                    model(configuration),
                )
                self.assertEqual(list(self.words("operations")), [1, 2])

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "7cd99d20de54b7a6fbe3f1d1c61777c886056bfdc86de88ee57b22e203f21663",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "d1425c446844ded48a8d5b22198152a4c1f27f01518c19d99b5d4775c9b335c4",
        )


if __name__ == "__main__":
    unittest.main()
