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
SOURCE = COMPONENT_ROOT / "spotmgr_timer_start.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_timer_start_host.c"

CLOCK = 1
READ = 2
WRITE = 3
CTRL0 = 0x400083E0
COMPARE0 = 0x400083E8
GLOBEN = 0x40008010
NVIC_ISER = 0xE000E108
UINT_MASK = 0xFFFFFFFF


def expected_events(
    delay: int,
    ctrl0: int,
    globen: int,
) -> list[tuple[int, int, int]]:
    clear_set = ctrl0 | 2
    clear_reset = clear_set & ~2
    return [
        (CLOCK, 4, 49),
        (WRITE, COMPARE0, (delay * 6) & UINT_MASK),
        (READ, GLOBEN, globen),
        (WRITE, GLOBEN, globen | 0x8000),
        (READ, CTRL0, ctrl0),
        (WRITE, CTRL0, clear_set),
        (READ, CTRL0, clear_set),
        (WRITE, CTRL0, clear_reset),
        (WRITE, NVIC_ISER, 0x40000),
        (READ, CTRL0, clear_reset),
        (WRITE, CTRL0, clear_reset | 1),
    ]


class SpotmgrTimerStartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_timer_start.dylib"
            if sys.platform == "darwin"
            else "spotmgr_timer_start.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_spotmgr_timer_start_reset
        cls.reset_fixture.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.reset_fixture.restype = None
        cls.start = cls.loaded.open_cfw_spotmgr_timer_start
        cls.start.argtypes = [ctypes.c_uint]
        cls.start.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_start_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 11).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_start_event_{name}",
        )

    def run_case(
        self,
        delay: int,
        ctrl0: int,
        globen: int,
        sentinel: int = 0xA5A55A5A,
        clock_result: int = 0,
    ) -> list[tuple[int, int, int]]:
        self.reset_fixture(ctrl0, globen, sentinel, clock_result)
        self.start(delay)
        return list(
            zip(
                self.words("kinds"),
                self.words("a"),
                self.words("b"),
            )
        )

    def test_exact_stock_transaction_order(self) -> None:
        delay = 0x12345678
        ctrl0 = 0x89ABCDEF
        globen = 0x10203040

        self.assertEqual(
            self.run_case(delay, ctrl0, globen),
            expected_events(delay, ctrl0, globen),
        )
        self.assertEqual(self.word("event_count").value, 11)

    def test_final_register_state_preserves_unrelated_bits(self) -> None:
        self.run_case(25, 0xFFFFFFFE, 0xFFFF7FFF)

        self.assertEqual(self.word("compare0").value, 150)
        self.assertEqual(self.word("globen").value, UINT_MASK)
        self.assertEqual(self.word("ctrl0").value, 0xFFFFFFFD)
        self.assertEqual(self.word("nvic_iser").value, 0x40000)

    def test_clear_bit_is_toggled_before_enable(self) -> None:
        events = self.run_case(1, 0xA5A55A5A, 0)

        self.assertEqual(
            events[4:8],
            [
                (READ, CTRL0, 0xA5A55A5A),
                (WRITE, CTRL0, 0xA5A55A5A),
                (READ, CTRL0, 0xA5A55A5A),
                (WRITE, CTRL0, 0xA5A55A58),
            ],
        )
        self.assertEqual(events[8], (WRITE, NVIC_ISER, 0x40000))
        self.assertEqual(events[9], (READ, CTRL0, 0xA5A55A58))
        self.assertEqual(events[10], (WRITE, CTRL0, 0xA5A55A59))

    def test_delay_scaling_wraps_as_unsigned_32_bit(self) -> None:
        self.run_case(0xFFFFFFFF, 0, 0)

        self.assertEqual(self.word("compare0").value, 0xFFFFFFFA)

    def test_clock_request_result_is_ignored(self) -> None:
        for result in (0, 1, 6, UINT_MASK):
            with self.subTest(result=result):
                events = self.run_case(50, 0, 0, clock_result=result)
                self.assertEqual(events, expected_events(50, 0, 0))

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x00480240)

        for _ in range(1000):
            delay = generator.getrandbits(32)
            ctrl0 = generator.getrandbits(32)
            globen = generator.getrandbits(32)
            clock_result = generator.getrandbits(32)
            self.assertEqual(
                self.run_case(
                    delay,
                    ctrl0,
                    globen,
                    clock_result=clock_result,
                ),
                expected_events(delay, ctrl0, globen),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c6dde040fcac2e16154950cd97a0640d"
            "9f8536619f52dba9faac8eb53374cafd",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "24f8ef14ebbd470efef191add5ca1e990"
            "4dfda80ade393dc02b0c05ebaa689a1",
        )


if __name__ == "__main__":
    unittest.main()
