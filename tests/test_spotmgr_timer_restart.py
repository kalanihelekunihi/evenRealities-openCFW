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
SOURCE = COMPONENT_ROOT / "spotmgr_timer_restart.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_timer_restart_host.c"

READ = 1
WRITE = 2
CTRL0 = 0x400083E0
COMPARE0 = 0x400083E8
INTCLR = 0x40008068
NVIC_ICPR = 0xE000E288
UINT_MASK = 0xFFFFFFFF


def expected_events(
    delay: int,
    ctrl0: int,
) -> list[tuple[int, int, int]]:
    disabled = ctrl0 & ~1
    clear_set = disabled | 2
    clear_reset = clear_set & ~2
    return [
        (READ, CTRL0, ctrl0),
        (WRITE, CTRL0, disabled),
        (READ, CTRL0, disabled),
        (WRITE, CTRL0, clear_set),
        (READ, CTRL0, clear_set),
        (WRITE, CTRL0, clear_reset),
        (WRITE, COMPARE0, (delay * 6) & UINT_MASK),
        (WRITE, INTCLR, 0xC0000000),
        (WRITE, NVIC_ICPR, 0x40000),
        (READ, CTRL0, clear_reset),
        (WRITE, CTRL0, clear_reset | 1),
    ]


class SpotmgrTimerRestartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_timer_restart.dylib"
            if sys.platform == "darwin"
            else "spotmgr_timer_restart.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_spotmgr_timer_restart_reset
        cls.reset_fixture.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.reset_fixture.restype = None
        cls.restart = cls.loaded.open_cfw_spotmgr_timer_restart
        cls.restart.argtypes = [ctypes.c_uint]
        cls.restart.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_restart_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 11).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_restart_event_{name}",
        )

    def run_case(
        self,
        delay: int,
        ctrl0: int,
        sentinel: int = 0xA5A55A5A,
    ) -> list[tuple[int, int, int]]:
        self.reset_fixture(ctrl0, sentinel)
        self.restart(delay)
        return list(
            zip(
                self.words("kinds"),
                self.words("addresses"),
                self.words("values"),
            )
        )

    def test_exact_stock_transaction_order(self) -> None:
        delay = 0x12345678
        ctrl0 = 0x89ABCDEF

        self.assertEqual(
            self.run_case(delay, ctrl0),
            expected_events(delay, ctrl0),
        )
        self.assertEqual(self.word("event_count").value, 11)

    def test_final_register_state_matches_stock(self) -> None:
        self.run_case(25, 0xFFFFFFFE)

        self.assertEqual(self.word("compare0").value, 150)
        self.assertEqual(self.word("intclr").value, 0xC0000000)
        self.assertEqual(self.word("nvic_icpr").value, 0x40000)
        self.assertEqual(self.word("ctrl0").value, 0xFFFFFFFD)

    def test_disable_and_clear_pulse_precede_compare_update(self) -> None:
        events = self.run_case(1, 0xA5A55A5B)

        self.assertEqual(
            events[:7],
            [
                (READ, CTRL0, 0xA5A55A5B),
                (WRITE, CTRL0, 0xA5A55A5A),
                (READ, CTRL0, 0xA5A55A5A),
                (WRITE, CTRL0, 0xA5A55A5A),
                (READ, CTRL0, 0xA5A55A5A),
                (WRITE, CTRL0, 0xA5A55A58),
                (WRITE, COMPARE0, 6),
            ],
        )

    def test_interrupt_clears_precede_final_enable(self) -> None:
        events = self.run_case(50, 0)

        self.assertEqual(events[7], (WRITE, INTCLR, 0xC0000000))
        self.assertEqual(events[8], (WRITE, NVIC_ICPR, 0x40000))
        self.assertEqual(events[9], (READ, CTRL0, 0))
        self.assertEqual(events[10], (WRITE, CTRL0, 1))

    def test_delay_scaling_wraps_as_unsigned_32_bit(self) -> None:
        self.run_case(UINT_MASK, 0)

        self.assertEqual(self.word("compare0").value, 0xFFFFFFFA)

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x0048028A)

        for _ in range(1000):
            delay = generator.getrandbits(32)
            ctrl0 = generator.getrandbits(32)
            self.assertEqual(
                self.run_case(delay, ctrl0),
                expected_events(delay, ctrl0),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1fa65b642ec18140598fe59d829aecb2"
            "23ff9437bb72e689f92d75781162ce4c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "30ea4fb1cc52796ff6eb368c7058166c"
            "34d587a6a5a9af2564a803073bb6cf17",
        )


if __name__ == "__main__":
    unittest.main()
