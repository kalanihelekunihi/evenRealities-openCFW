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
SOURCE = COMPONENT_ROOT / "pwrctrl_temp_update.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_temp_update_host.c"
)

UINT_MASK = 0xFFFFFFFF


class PwrctrlTempUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_temp_update.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_temp_update.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_pwrctrl_temp_reset
        cls.reset_fixture.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.reset_fixture.restype = None
        cls.call = cls.loaded.open_cfw_test_pwrctrl_temp_call
        cls.call.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
        ]
        cls.call.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_pwrctrl_temp_{name}",
        )

    def run_case(
        self,
        temperature_bits: int,
        status: int = 0,
        lower_bits: int = 0xC1200000,
        higher_bits: int = 0x42500000,
    ) -> tuple[int, tuple[int, int]]:
        thresholds = (ctypes.c_uint * 2)(0xAAAAAAAA, 0x55555555)
        self.reset_fixture(status, lower_bits, higher_bits)
        result = self.call(temperature_bits, thresholds)
        return result, tuple(thresholds)

    def test_success_forwards_temperature_and_copies_threshold_bits(
        self,
    ) -> None:
        result, thresholds = self.run_case(0x42360000)

        self.assertEqual(result, 0)
        self.assertEqual(thresholds, (0xC1200000, 0x42500000))
        self.assertEqual(self.word("stimulus").value, 2)
        self.assertEqual(self.word("enabled").value, 0)
        self.assertEqual(self.word("input_bits").value, 0x42360000)
        self.assertEqual(self.word("call_count").value, 1)

    def test_every_nonzero_backend_status_returns_one_and_zeroes_outputs(
        self,
    ) -> None:
        for status in (1, 2, 0x80000000, UINT_MASK):
            with self.subTest(status=status):
                result, thresholds = self.run_case(
                    0xC2480000,
                    status=status,
                )
                self.assertEqual(result, 1)
                self.assertEqual(thresholds, (0, 0))
                self.assertEqual(self.word("call_count").value, 1)

    def test_success_preserves_signed_zero_infinity_and_nan_payload_bits(
        self,
    ) -> None:
        for lower_bits, higher_bits in (
            (0x80000000, 0x7F800000),
            (0xFF800000, 0x7FC12345),
            (0xFFC54321, 0x00000001),
        ):
            with self.subTest(
                lower_bits=lower_bits,
                higher_bits=higher_bits,
            ):
                result, thresholds = self.run_case(
                    0x3F800000,
                    lower_bits=lower_bits,
                    higher_bits=higher_bits,
                )
                self.assertEqual(result, 0)
                self.assertEqual(thresholds, (lower_bits, higher_bits))

    def test_backend_is_called_before_outputs_are_selected(self) -> None:
        result, thresholds = self.run_case(
            0x00000000,
            lower_bits=0x11111111,
            higher_bits=0x22222222,
        )

        self.assertEqual(result, 0)
        self.assertEqual(thresholds, (0x11111111, 0x22222222))
        self.assertEqual(self.word("call_count").value, 1)

    def test_randomized_bit_exact_success_and_failure_model(self) -> None:
        generator = random.Random(0x00480028)

        for _ in range(1000):
            temperature_bits = generator.getrandbits(32)
            lower_bits = generator.getrandbits(32)
            higher_bits = generator.getrandbits(32)
            status = generator.getrandbits(32)
            result, thresholds = self.run_case(
                temperature_bits,
                status=status,
                lower_bits=lower_bits,
                higher_bits=higher_bits,
            )
            self.assertEqual(self.word("input_bits").value, temperature_bits)
            self.assertEqual(self.word("stimulus").value, 2)
            self.assertEqual(self.word("enabled").value, 0)
            self.assertEqual(self.word("call_count").value, 1)
            if status == 0:
                self.assertEqual(result, 0)
                self.assertEqual(
                    thresholds,
                    (lower_bits, higher_bits),
                )
            else:
                self.assertEqual(result, 1)
                self.assertEqual(thresholds, (0, 0))

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "6418e3f1afb647b0d268e3c489f89d9f9a34ef33f0fc4598e0a3f2c6c6a4b794",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "065bf91f1d09931245118282da1f7ae282badbb9183b456e4cef080a74d8f1f9",
        )


if __name__ == "__main__":
    unittest.main()
