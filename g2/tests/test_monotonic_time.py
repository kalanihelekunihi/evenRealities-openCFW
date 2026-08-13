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
SOURCE = COMPONENT_ROOT / "monotonic_time.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "monotonic_time_host.c"
UINT_MASK = (1 << 32) - 1


class MonotonicTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "monotonic_time.dylib"
            if sys.platform == "darwin"
            else "monotonic_time.so"
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
        cls.seconds = cls.loaded.open_cfw_monotonic_seconds
        cls.seconds.argtypes = []
        cls.seconds.restype = ctypes.c_uint
        cls.trace = (
            ctypes.c_uint * 8
        ).in_dll(cls.loaded, "open_cfw_test_monotonic_trace")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    def reset(
        self,
        *,
        last_tick: int,
        wraps: int,
        tick: int,
        primask: int = 0,
    ) -> None:
        for name, value in (
            ("open_cfw_test_monotonic_last_tick", last_tick),
            ("open_cfw_test_monotonic_wrap_count", wraps),
            ("open_cfw_test_monotonic_tick_result", tick),
            ("open_cfw_test_monotonic_prior_primask", primask),
        ):
            self.word(name).value = value & UINT_MASK
        for name in (
            "open_cfw_test_monotonic_restored_primask",
            "open_cfw_test_monotonic_irq_disable_calls",
            "open_cfw_test_monotonic_irq_restore_calls",
            "open_cfw_test_monotonic_tick_calls",
            "open_cfw_test_monotonic_divmod_calls",
            "open_cfw_test_monotonic_dividend_low",
            "open_cfw_test_monotonic_dividend_high",
            "open_cfw_test_monotonic_divisor_low",
            "open_cfw_test_monotonic_divisor_high",
            "open_cfw_test_monotonic_trace_count",
        ):
            self.word(name).value = 0
        self.trace[:] = [0] * 8

    def assert_run(self, *, expected_wraps: int, tick: int) -> None:
        extended = ((expected_wraps & UINT_MASK) << 32) | tick
        self.assertEqual(self.seconds(), (extended // 1000) & UINT_MASK)
        self.assertEqual(
            self.word("open_cfw_test_monotonic_last_tick").value,
            tick,
        )
        self.assertEqual(
            self.word("open_cfw_test_monotonic_wrap_count").value,
            expected_wraps & UINT_MASK,
        )
        self.assertEqual(
            self.word("open_cfw_test_monotonic_dividend_low").value,
            tick,
        )
        self.assertEqual(
            self.word("open_cfw_test_monotonic_dividend_high").value,
            expected_wraps & UINT_MASK,
        )
        self.assertEqual(
            self.word("open_cfw_test_monotonic_divisor_low").value,
            1000,
        )
        self.assertEqual(
            self.word("open_cfw_test_monotonic_divisor_high").value,
            0,
        )
        self.assertEqual(
            self.trace[
                :self.word("open_cfw_test_monotonic_trace_count").value
            ],
            [1, 2, 3, 4],
        )
        for name in (
            "open_cfw_test_monotonic_irq_disable_calls",
            "open_cfw_test_monotonic_irq_restore_calls",
            "open_cfw_test_monotonic_tick_calls",
            "open_cfw_test_monotonic_divmod_calls",
        ):
            self.assertEqual(self.word(name).value, 1)

    def test_nonwrapping_tick_extends_and_divides_after_restore(self) -> None:
        self.reset(
            last_tick=1234,
            wraps=7,
            tick=5678,
            primask=1,
        )
        self.assert_run(expected_wraps=7, tick=5678)
        self.assertEqual(
            self.word("open_cfw_test_monotonic_restored_primask").value,
            1,
        )

    def test_lower_tick_increments_wrap_count_with_unsigned_wrap(self) -> None:
        self.reset(last_tick=0xFFFFFFFE, wraps=11, tick=2)
        self.assert_run(expected_wraps=12, tick=2)

        self.reset(last_tick=9, wraps=UINT_MASK, tick=8)
        self.assert_run(expected_wraps=0, tick=8)

    def test_equal_tick_does_not_increment_wrap_count(self) -> None:
        self.reset(last_tick=0xA5A5A5A5, wraps=3, tick=0xA5A5A5A5)
        self.assert_run(expected_wraps=3, tick=0xA5A5A5A5)

    def test_randomized_model(self) -> None:
        generator = random.Random(0x0047DC74)
        for _ in range(500):
            last_tick = generator.getrandbits(32)
            wraps = generator.getrandbits(32)
            tick = generator.getrandbits(32)
            expected_wraps = (
                wraps + int(tick < last_tick)
            ) & UINT_MASK
            self.reset(
                last_tick=last_tick,
                wraps=wraps,
                tick=tick,
                primask=generator.getrandbits(1),
            )
            self.assert_run(expected_wraps=expected_wraps, tick=tick)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0135fccd34e034e1ee4c0dffacac51ea12531b8c8bc6f6431a4d8f979e8a8baf",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "3b0a04409ce9611cd6a1b4e913f43fc6fc38ce292dc0016f540e7ac5c97ac8c1",
        )


if __name__ == "__main__":
    unittest.main()
