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
SOURCE = COMPONENT_ROOT / "rtc_time_get.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtc_time_get_host.c"

EVENT_READ = 1
EVENT_WRITE = 2
EVENT_IRQ_DISABLE = 3
EVENT_IRQ_RESTORE = 4
EVENT_DELAY = 5

CLKGEN_OCTRL = 0x4000400C
RTC_COUNTER_LOW = 0x40004820
RTC_COUNTER_UP = 0x40004824
TIMER_CONTROL = 0x400083C0
TIMER_COUNTER = 0x400083C4
TIMER_COMPARE0 = 0x400083C8
TIMER_COMPARE1 = 0x400083CC
TIMER_GLOBAL_ENABLE = 0x40008010


class RtcTime(ctypes.Structure):
    _fields_ = [
        ("read_error", ctypes.c_uint),
        ("weekday", ctypes.c_uint),
        ("century_bit", ctypes.c_uint),
        ("year", ctypes.c_uint),
        ("month", ctypes.c_uint),
        ("day", ctypes.c_uint),
        ("hour", ctypes.c_uint),
        ("minute", ctypes.c_uint),
        ("second", ctypes.c_uint),
        ("hundredths", ctypes.c_uint),
    ]


def bcd_to_decimal(value: int) -> int:
    byte = value & 0xFF
    return (byte >> 4) * 10 + (byte & 0xF)


def expected_time(low: int, up: int) -> tuple[int, ...]:
    return (
        up >> 31,
        bcd_to_decimal((up >> 24) & 7),
        (up >> 28) & 1,
        bcd_to_decimal((up >> 16) & 0xFF),
        bcd_to_decimal((up >> 8) & 0x1F),
        bcd_to_decimal(up & 0x3F),
        bcd_to_decimal((low >> 24) & 0x3F),
        bcd_to_decimal((low >> 16) & 0x7F),
        bcd_to_decimal((low >> 8) & 0x7F),
        bcd_to_decimal(low & 0xFF),
    )


class RtcTimeGetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtc_time_get.dylib"
            if sys.platform == "darwin"
            else "rtc_time_get.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtc_get_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.get_time = cls.loaded.open_cfw_rtc_time_get
        cls.get_time.argtypes = [ctypes.POINTER(RtcTime)]
        cls.get_time.restype = None
        cls.event_kind = (
            ctypes.c_uint * 128
        ).in_dll(cls.loaded, "open_cfw_test_rtc_get_event_kind")
        cls.event_address = (
            ctypes.c_uint * 128
        ).in_dll(cls.loaded, "open_cfw_test_rtc_get_event_address")
        cls.event_value = (
            ctypes.c_uint * 128
        ).in_dll(cls.loaded, "open_cfw_test_rtc_get_event_value")
        cls.timer_values = (
            ctypes.c_uint * 32
        ).in_dll(cls.loaded, "open_cfw_test_rtc_get_timer_values")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtc_get_{name}",
        )

    def events(self) -> list[tuple[int, int, int]]:
        count = self.word("event_count").value
        return [
            (
                self.event_kind[index],
                self.event_address[index],
                self.event_value[index],
            )
            for index in range(count)
        ]

    def set_timer_values(self, *values: int) -> None:
        self.word("timer_value_count").value = len(values)
        self.word("timer_value_index").value = 0
        for index, value in enumerate(values):
            self.timer_values[index] = value

    @staticmethod
    def values(time: RtcTime) -> tuple[int, ...]:
        return tuple(
            getattr(time, field_name)
            for field_name, _ in RtcTime._fields_
        )

    def test_exact_xtal_sequence_and_decoded_time(self) -> None:
        self.word("timer_control").value = 0xA5A50001
        self.word("timer_global_enable").value = 0x12340020
        self.word("clock_control").value = 0x00000000
        self.word("counter_low").value = 0x23595876
        self.word("counter_up").value = 0x14240229
        self.word("primask").value = 1
        self.set_timer_values(0x1234, 0x1235)
        output = RtcTime(*(0xDEADBEEF for _ in range(10)))

        self.get_time(ctypes.byref(output))

        self.assertEqual(
            self.values(output),
            (0, 4, 1, 24, 2, 29, 23, 59, 58, 76),
        )
        self.assertEqual(
            self.events(),
            [
                (EVENT_IRQ_DISABLE, 0, 1),
                (EVENT_READ, TIMER_CONTROL, 0xA5A50001),
                (EVENT_WRITE, TIMER_CONTROL, 0xA5A50000),
                (EVENT_READ, CLKGEN_OCTRL, 0),
                (EVENT_WRITE, TIMER_CONTROL, 0xA10),
                (EVENT_WRITE, TIMER_COMPARE0, 0xFFFFFFFF),
                (EVENT_WRITE, TIMER_COMPARE1, 0xFFFFFFFF),
                (EVENT_READ, TIMER_GLOBAL_ENABLE, 0x12340020),
                (EVENT_WRITE, TIMER_GLOBAL_ENABLE, 0x12344020),
                (EVENT_READ, TIMER_CONTROL, 0xA10),
                (EVENT_WRITE, TIMER_CONTROL, 0xA12),
                (EVENT_READ, TIMER_CONTROL, 0xA12),
                (EVENT_WRITE, TIMER_CONTROL, 0xA10),
                (EVENT_READ, TIMER_CONTROL, 0xA10),
                (EVENT_WRITE, TIMER_CONTROL, 0xA11),
                (EVENT_READ, TIMER_COUNTER, 0x1234),
                (EVENT_READ, TIMER_COUNTER, 0x1235),
                (EVENT_READ, TIMER_CONTROL, 0xA11),
                (EVENT_WRITE, TIMER_CONTROL, 0xA10),
                (EVENT_DELAY, 0, 10),
                (EVENT_READ, RTC_COUNTER_LOW, 0x23595876),
                (EVENT_READ, RTC_COUNTER_UP, 0x14240229),
                (EVENT_IRQ_RESTORE, 0, 1),
            ],
        )

    def test_lfrc_path_and_repeated_edge_poll(self) -> None:
        self.word("clock_control").value = 0x80
        self.word("timer_global_enable").value = 0xFFFFFFFF
        self.word("primask").value = 0xFFFFFFFF
        self.word("counter_low").value = 0x01020304
        self.word("counter_up").value = 0x11050607
        self.set_timer_values(9, 9, 9, 10)
        output = RtcTime()

        self.get_time(ctypes.byref(output))

        self.assertEqual(self.word("timer_control").value, 0x610)
        self.assertEqual(self.word("timer_compare0").value, 0xFFFFFFFF)
        self.assertEqual(self.word("timer_compare1").value, 0xFFFFFFFF)
        self.assertEqual(
            [
                event
                for event in self.events()
                if event[1] == TIMER_COUNTER
            ],
            [
                (EVENT_READ, TIMER_COUNTER, 9),
                (EVENT_READ, TIMER_COUNTER, 9),
                (EVENT_READ, TIMER_COUNTER, 9),
                (EVENT_READ, TIMER_COUNTER, 10),
            ],
        )
        self.assertEqual(self.events()[-1], (EVENT_IRQ_RESTORE, 0, 0xFFFFFFFF))

    def test_read_error_preserves_all_other_output_fields(self) -> None:
        self.word("counter_low").value = 0xFFFFFFFF
        self.word("counter_up").value = 0xFFFFFFFF
        initial = tuple(0x1000 + index for index in range(10))
        output = RtcTime(*initial)

        self.get_time(ctypes.byref(output))

        self.assertEqual(
            self.values(output),
            (1,) + initial[1:],
        )
        self.assertLess(
            next(
                index
                for index, event in enumerate(self.events())
                if event[1] == RTC_COUNTER_UP
            ),
            next(
                index
                for index, event in enumerate(self.events())
                if event[0] == EVENT_IRQ_RESTORE
            ),
        )

    def test_randomized_raw_bcd_decode_matches_stock_model(self) -> None:
        generator = random.Random(0x0047EF10)

        for _ in range(500):
            self.reset_fixture()
            low = generator.getrandbits(32)
            up = generator.getrandbits(31)
            self.word("counter_low").value = low
            self.word("counter_up").value = up
            self.word("clock_control").value = (
                0x80 if generator.getrandbits(1) else 0
            )
            self.word("primask").value = generator.getrandbits(32)
            edge = generator.getrandbits(32)
            self.set_timer_values(edge, edge, edge + 1)
            output = RtcTime(*(generator.getrandbits(32) for _ in range(10)))

            self.get_time(ctypes.byref(output))

            self.assertEqual(self.values(output), expected_time(low, up))
            self.assertEqual(
                self.events()[-1],
                (EVENT_IRQ_RESTORE, 0, self.word("primask").value),
            )

    def test_stock_register_addresses_are_present(self) -> None:
        source = SOURCE.read_text()
        for address in (
            "0x4000400CU",
            "0x40004820U",
            "0x40004824U",
            "0x400083C0U",
            "0x400083C4U",
            "0x400083C8U",
            "0x400083CCU",
            "0x40008010U",
        ):
            self.assertIn(address, source)
        self.assertIn("open_cfw_lv_irq_disable()", source)
        self.assertIn("open_cfw_delay_us(microseconds)", source)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "f7a3f5b0887ceff89480413040fc9a21d5bb78ca0a165fc8eb87cb5258f6d3a3",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5ed6918e623d1a47247bcdc96178d9cf09f1ad3f0e99f1152f7a5e79ac2df32e",
        )


if __name__ == "__main__":
    unittest.main()
