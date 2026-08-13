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
SOURCE = COMPONENT_ROOT / "pwrctrl_crypto_quiesce.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "pwrctrl_crypto_quiesce_host.c"
)


class PwrctrlCryptoQuiesceTests(unittest.TestCase):
    STATUS = 1
    READ = 2
    WRITE = 3

    MRAM_CONTROL = 0x40020180
    IDLE = 0x400C0A7C
    POWERDOWN = 0x400C0A80

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_crypto_quiesce.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_crypto_quiesce.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_crypto_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.quiesce = cls.loaded.open_cfw_pwrctrl_crypto_quiesce
        cls.quiesce.argtypes = []
        cls.quiesce.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, f"open_cfw_test_crypto_{name}")

    @classmethod
    def words(cls, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(
            cls.loaded,
            f"open_cfw_test_crypto_{name}",
        )

    def set_results(self, *values: int) -> None:
        results = self.words("results", 3)
        for index, value in enumerate(values):
            results[index] = value
        self.word("result_count").value = len(values)

    def trace(self) -> list[tuple[int, int]]:
        count = min(self.word("trace_count").value, 8)
        events = self.words("trace_event", 8)
        values = self.words("trace_value", 8)
        return [(events[index], values[index]) for index in range(count)]

    def test_already_ready_returns_without_touching_crypto(self) -> None:
        self.word("powerdown").value = 0xA5A5A5A4
        self.set_results(0)

        self.assertEqual(self.quiesce(), 0)

        self.assertEqual(self.word("calls").value, 1)
        self.assertEqual(self.word("powerdown").value, 0xA5A5A5A4)
        self.assertEqual(self.word("reads").value, 0)
        self.assertEqual(self.word("writes").value, 0)
        self.assertEqual(self.trace(), [(self.STATUS, self.MRAM_CONTROL)])

    def test_idle_failure_is_propagated_without_powerdown_write(self) -> None:
        self.set_results(4, 9)

        self.assertEqual(self.quiesce(), 9)

        self.assertEqual(self.word("calls").value, 2)
        self.assertEqual(self.word("reads").value, 0)
        self.assertEqual(self.word("writes").value, 0)
        self.assertEqual(
            self.trace(),
            [
                (self.STATUS, self.MRAM_CONTROL),
                (self.STATUS, self.IDLE),
            ],
        )

    def test_idle_recovery_sets_bit_then_returns_final_result(self) -> None:
        self.word("powerdown").value = 0xFFFFFFFE
        self.set_results(4, 0, 7)

        self.assertEqual(self.quiesce(), 7)

        self.assertEqual(self.word("powerdown").value, 0xFFFFFFFF)
        self.assertEqual(self.word("reads").value, 1)
        self.assertEqual(self.word("writes").value, 1)
        self.assertEqual(
            self.trace(),
            [
                (self.STATUS, self.MRAM_CONTROL),
                (self.STATUS, self.IDLE),
                (self.READ, self.POWERDOWN),
                (self.WRITE, 0xFFFFFFFF),
                (self.STATUS, self.MRAM_CONTROL),
            ],
        )

    def test_status_change_arguments_are_exact(self) -> None:
        self.set_results(1, 0, 0)

        self.assertEqual(self.quiesce(), 0)

        self.assertEqual(list(self.words("wait", 3)), [100, 100, 100])
        self.assertEqual(
            list(self.words("address", 3)),
            [self.MRAM_CONTROL, self.IDLE, self.MRAM_CONTROL],
        )
        self.assertEqual(list(self.words("mask", 3)), [0x100, 1, 0x100])
        self.assertEqual(list(self.words("expected", 3)), [0x100, 1, 0x100])

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x47F56E)

        for _ in range(1000):
            self.reset_fixture()
            first = generator.getrandbits(32)
            second = generator.getrandbits(32)
            third = generator.getrandbits(32)
            powerdown = generator.getrandbits(32)
            self.word("powerdown").value = powerdown
            self.set_results(first, second, third)

            result = self.quiesce()

            if first == 0:
                self.assertEqual(result, 0)
                self.assertEqual(self.word("calls").value, 1)
                self.assertEqual(self.word("powerdown").value, powerdown)
            elif second != 0:
                self.assertEqual(result, second)
                self.assertEqual(self.word("calls").value, 2)
                self.assertEqual(self.word("powerdown").value, powerdown)
            else:
                self.assertEqual(result, third)
                self.assertEqual(self.word("calls").value, 3)
                self.assertEqual(
                    self.word("powerdown").value,
                    powerdown | 1,
                )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0e8789ead970a9f2c22a560198fed85dd06752c74086b9823425c871cf5448e7",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "46e5261ecb9bb4cf6af593c3a66ac841ac89d22619c76046c90629623c3f6e78",
        )


if __name__ == "__main__":
    unittest.main()
