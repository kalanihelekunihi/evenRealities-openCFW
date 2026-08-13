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
SOURCE = COMPONENT_ROOT / "spotmgr_timer_stop.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "spotmgr_timer_stop_host.c"

CLOCK = 1
READ = 2
WRITE = 3
CTRL0 = 0x400083E0
GLOBEN = 0x40008010
INTCLR = 0x40008068
NVIC_ICER = 0xE000E188
NVIC_ICPR = 0xE000E288
SYSBUS_FLUSH = 0x47FF0000
UINT_MASK = 0xFFFFFFFF


def expected_events(
    ctrl0: int,
    globen: int,
    sysbus_flush: int,
) -> list[tuple[int, int, int]]:
    return [
        (READ, CTRL0, ctrl0),
        (WRITE, CTRL0, ctrl0 & ~1),
        (READ, GLOBEN, globen),
        (WRITE, GLOBEN, globen & ~0x8000),
        (CLOCK, 4, 49),
        (WRITE, NVIC_ICER, 0x40000),
        (WRITE, INTCLR, 0xC0000000),
        (READ, SYSBUS_FLUSH, sysbus_flush),
        (WRITE, NVIC_ICPR, 0x40000),
    ]


class SpotmgrTimerStopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "spotmgr_timer_stop.dylib"
            if sys.platform == "darwin"
            else "spotmgr_timer_stop.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_spotmgr_timer_stop_reset
        cls.reset_fixture.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.reset_fixture.restype = None
        cls.stop = cls.loaded.open_cfw_spotmgr_timer_stop
        cls.stop.argtypes = []
        cls.stop.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_stop_{name}",
        )

    @classmethod
    def words(cls, name: str) -> ctypes.Array:
        return (ctypes.c_uint * 9).in_dll(
            cls.loaded,
            f"open_cfw_test_spotmgr_timer_stop_event_{name}",
        )

    def run_case(
        self,
        ctrl0: int,
        globen: int,
        sysbus_flush: int,
        sentinel: int = 0xA5A55A5A,
        clock_result: int = 0,
    ) -> list[tuple[int, int, int]]:
        self.reset_fixture(
            ctrl0,
            globen,
            sysbus_flush,
            sentinel,
            clock_result,
        )
        self.stop()
        return list(
            zip(
                self.words("kinds"),
                self.words("a"),
                self.words("b"),
            )
        )

    def test_exact_stock_transaction_order(self) -> None:
        ctrl0 = 0x89ABCDEF
        globen = 0x1020B040
        sysbus_flush = 0x76543210

        self.assertEqual(
            self.run_case(ctrl0, globen, sysbus_flush),
            expected_events(ctrl0, globen, sysbus_flush),
        )
        self.assertEqual(self.word("event_count").value, 9)

    def test_final_register_state_preserves_unrelated_bits(self) -> None:
        self.run_case(UINT_MASK, UINT_MASK, 0x12345678)

        self.assertEqual(self.word("ctrl0").value, 0xFFFFFFFE)
        self.assertEqual(self.word("globen").value, 0xFFFF7FFF)
        self.assertEqual(self.word("nvic_icer").value, 0x40000)
        self.assertEqual(self.word("intclr").value, 0xC0000000)
        self.assertEqual(self.word("nvic_icpr").value, 0x40000)

    def test_disable_operations_precede_clock_release(self) -> None:
        events = self.run_case(3, 0x8001, 0)

        self.assertEqual(
            events[:5],
            [
                (READ, CTRL0, 3),
                (WRITE, CTRL0, 2),
                (READ, GLOBEN, 0x8001),
                (WRITE, GLOBEN, 1),
                (CLOCK, 4, 49),
            ],
        )

    def test_bus_flush_separates_interrupt_clear_and_pending_clear(self) -> None:
        events = self.run_case(0, 0, 0xDEADBEEF)

        self.assertEqual(events[5], (WRITE, NVIC_ICER, 0x40000))
        self.assertEqual(events[6], (WRITE, INTCLR, 0xC0000000))
        self.assertEqual(events[7], (READ, SYSBUS_FLUSH, 0xDEADBEEF))
        self.assertEqual(events[8], (WRITE, NVIC_ICPR, 0x40000))

    def test_clock_release_result_is_ignored(self) -> None:
        for result in (0, 1, 6, UINT_MASK):
            with self.subTest(result=result):
                events = self.run_case(
                    0xA5A55A5B,
                    0x12348000,
                    0xCAFEBABE,
                    clock_result=result,
                )
                self.assertEqual(
                    events,
                    expected_events(
                        0xA5A55A5B,
                        0x12348000,
                        0xCAFEBABE,
                    ),
                )

    def test_randomized_stock_model(self) -> None:
        generator = random.Random(0x004802CE)

        for _ in range(1000):
            ctrl0 = generator.getrandbits(32)
            globen = generator.getrandbits(32)
            sysbus_flush = generator.getrandbits(32)
            clock_result = generator.getrandbits(32)
            self.assertEqual(
                self.run_case(
                    ctrl0,
                    globen,
                    sysbus_flush,
                    clock_result=clock_result,
                ),
                expected_events(ctrl0, globen, sysbus_flush),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ae1fef1881c8b5353bbf7bb79c30ce77"
            "0e5f7ce33865b38cdb752c94e2ed5581",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ac526db5c2e939c60fc0b893f7ba5749"
            "bb4546f8305780619c3451fd00620108",
        )


if __name__ == "__main__":
    unittest.main()
