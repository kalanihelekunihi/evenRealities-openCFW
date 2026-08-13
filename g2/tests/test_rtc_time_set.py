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
SOURCE = COMPONENT_ROOT / "rtc_time_set.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtc_time_set_host.c"

UINT_MASK = (1 << 32) - 1
RTC_CONTROL = 0x40004800
RTC_COUNTER_LOW = 0x40004820
RTC_COUNTER_UP = 0x40004824

EVENT_READ = 1
EVENT_WRITE = 2
EVENT_LEVEL = 3
EVENT_STRUCTURED = 4
EVENT_TRACE = 5

TAG_ADDRESS = 0x0078D4A4
FILE_ADDRESS = 0x007149A4
FUNCTION_ADDRESS = 0x00785D30
MESSAGE_ADDRESS = 0x0077F180
TRACE_ADDRESS = 0x0075FA90

DAYS_PER_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
MONTH_OFFSETS = (4, 0, 0, 3, 5, 1, 3, 6, 2, 4, 0, 2)


class ApplicationTime(ctypes.Structure):
    _fields_ = [
        ("prefix0", ctypes.c_uint),
        ("prefix1", ctypes.c_uint),
        ("prefix2", ctypes.c_uint),
        ("year", ctypes.c_uint),
        ("month", ctypes.c_uint),
        ("day", ctypes.c_uint),
        ("hour", ctypes.c_uint),
        ("minute", ctypes.c_uint),
        ("second", ctypes.c_uint),
        ("subseconds", ctypes.c_uint),
    ]


def sdk_is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (
        year % 100 != 0 or year % 400 != 0
    )


def sdk_weekday(year: int, month: int, day: int) -> int:
    if month < 1 or month > 12 or year < 0 or day < 1:
        return 7
    if day > DAYS_PER_MONTH[month - 1]:
        if not (
            month == 2
            and sdk_is_leap_year(year)
            and day == 29
        ):
            return 7
    leap_offset = -1 if sdk_is_leap_year(year) and month < 3 else 0
    return (
        day
        + 2
        + year
        + year // 4
        - year // 100
        + year // 400
        + MONTH_OFFSETS[month - 1]
        + leap_offset
    ) % 7


def bcd(value: int) -> int:
    byte = value & 0xFF
    return byte % 10 | ((byte // 10 & 0xF) << 4)


def expected_registers(time: ApplicationTime) -> tuple[int, int] | None:
    weekday = sdk_weekday(time.year + 2000, time.month, time.day)
    if (
        time.second >= 60
        or time.minute >= 60
        or time.hour >= 24
        or time.day < 1
        or time.day > 31
        or time.month < 1
        or time.month > 12
        or time.year > 100
        or weekday > 6
    ):
        return None
    low = (
        ((bcd(time.hour) & 0x3F) << 24)
        | ((bcd(time.minute) & 0x7F) << 16)
        | ((bcd(time.second) & 0x7F) << 8)
    )
    up = (
        (1 << 28)
        | ((weekday & 7) << 24)
        | ((bcd(time.year) & 0xFF) << 16)
        | ((bcd(time.month) & 0x1F) << 8)
        | (bcd(time.day) & 0x3F)
    )
    return low, up


class RtcTimeSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtc_time_set.dylib"
            if sys.platform == "darwin"
            else "rtc_time_set.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtc_time_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_time = cls.loaded.open_cfw_rtc_time_set
        cls.set_time.argtypes = [ctypes.POINTER(ApplicationTime)]
        cls.set_time.restype = ctypes.c_uint
        cls.event_kind = (
            ctypes.c_uint * 32
        ).in_dll(cls.loaded, "open_cfw_test_rtc_time_event_kind")
        cls.event_address = (
            ctypes.c_uint * 32
        ).in_dll(cls.loaded, "open_cfw_test_rtc_time_event_address")
        cls.event_value = (
            ctypes.c_uint * 32
        ).in_dll(cls.loaded, "open_cfw_test_rtc_time_event_value")
        cls.level_values = (
            ctypes.c_uint * 8
        ).in_dll(cls.loaded, "open_cfw_test_rtc_time_level_values")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtc_time_{name}",
        )

    @classmethod
    def pointer_word(cls, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtc_time_{name}",
        )

    def set_levels(self, *values: int) -> None:
        self.word("level_count").value = len(values)
        for index, value in enumerate(values):
            self.level_values[index] = value

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

    @staticmethod
    def time(
        year: int = 24,
        month: int = 2,
        day: int = 29,
        hour: int = 23,
        minute: int = 59,
        second: int = 58,
    ) -> ApplicationTime:
        return ApplicationTime(
            0x11111111,
            0x22222222,
            0x33333333,
            year,
            month,
            day,
            hour,
            minute,
            second,
            0xFFFFFFFF,
        )

    def test_exact_valid_register_sequence_and_ignored_fields(self) -> None:
        value = self.time()
        self.word("control").value = 0xA5A5A5A5
        self.word("counter_low").value = 0xDEADBEEF
        self.word("counter_up").value = 0xCAFEBABE

        self.assertEqual(self.set_time(ctypes.byref(value)), 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_READ, RTC_CONTROL, 0xA5A5A5A5),
                (EVENT_WRITE, RTC_CONTROL, 0xA5A5A5A5),
                (EVENT_WRITE, RTC_COUNTER_LOW, 0x23595800),
                (EVENT_WRITE, RTC_COUNTER_UP, 0x14240229),
                (EVENT_READ, RTC_CONTROL, 0xA5A5A5A5),
                (EVENT_WRITE, RTC_CONTROL, 0xA5A5A5A4),
            ],
        )
        self.assertEqual(self.word("counter_low").value, 0x23595800)
        self.assertEqual(self.word("counter_up").value, 0x14240229)
        self.assertEqual(self.word("level_index").value, 0)

    def test_randomized_calendar_and_bcd_model(self) -> None:
        generator = random.Random(0x0047EE78)

        for _ in range(500):
            value = ApplicationTime(
                generator.getrandbits(32),
                generator.getrandbits(32),
                generator.getrandbits(32),
                generator.randrange(0, 101),
                generator.randrange(1, 13),
                generator.randrange(1, 32),
                generator.randrange(0, 24),
                generator.randrange(0, 60),
                generator.randrange(0, 60),
                generator.getrandbits(32),
            )
            expected = expected_registers(value)
            self.reset_fixture()
            initial_control = generator.getrandbits(32)
            self.word("control").value = initial_control

            result = self.set_time(ctypes.byref(value))
            self.assertEqual(result, 1 if expected is None else 0)
            if expected is None:
                self.assertEqual(
                    [event[0] for event in self.events()],
                    [EVENT_LEVEL, EVENT_LEVEL, EVENT_LEVEL],
                )
                continue

            low, up = expected
            self.assertEqual(self.word("counter_low").value, low)
            self.assertEqual(self.word("counter_up").value, up)
            self.assertEqual(
                self.word("control").value,
                initial_control & ~1 & UINT_MASK,
            )
            self.assertEqual(self.word("level_index").value, 0)

    def test_invalid_fields_and_dates_never_touch_rtc(self) -> None:
        cases = (
            {"year": 101},
            {"month": 0},
            {"month": 13},
            {"day": 0},
            {"day": 32},
            {"hour": 24},
            {"minute": 60},
            {"second": 60},
            {"year": 1, "month": 2, "day": 29},
            {"year": 24, "month": 2, "day": 30},
            {"year": 24, "month": 4, "day": 31},
        )
        for changes in cases:
            with self.subTest(**changes):
                self.reset_fixture()
                value = self.time()
                for name, field_value in changes.items():
                    setattr(value, name, field_value)
                self.set_levels(0, 0, 0)
                self.assertEqual(self.set_time(ctypes.byref(value)), 1)
                self.assertEqual(
                    self.events(),
                    [
                        (EVENT_LEVEL, 0, 0),
                        (EVENT_LEVEL, 0, 0),
                        (EVENT_LEVEL, 0, 0),
                    ],
                )

    def test_sdk_century_leap_behavior_is_preserved(self) -> None:
        year_2000 = self.time(year=0, month=2, day=29)
        self.set_levels(0, 0, 0)
        self.assertEqual(self.set_time(ctypes.byref(year_2000)), 1)

        self.reset_fixture()
        year_2100 = self.time(year=100, month=2, day=29)
        expected = expected_registers(year_2100)
        self.assertIsNotNone(expected)
        self.assertEqual(self.set_time(ctypes.byref(year_2100)), 0)
        self.assertEqual(
            (
                self.word("counter_low").value,
                self.word("counter_up").value,
            ),
            expected,
        )

    def test_failure_diagnostic_gates_and_metadata(self) -> None:
        invalid = self.time(month=0)

        self.set_levels(2, 1)
        self.assertEqual(self.set_time(ctypes.byref(invalid)), 1)
        self.assertEqual(
            [event[0] for event in self.events()],
            [EVENT_LEVEL, EVENT_STRUCTURED, EVENT_LEVEL, EVENT_TRACE],
        )
        self.assertEqual(self.word("structured_count").value, 1)
        self.assertEqual(self.word("structured_severity").value, 1)
        self.assertEqual(self.pointer_word("structured_tag").value, TAG_ADDRESS)
        self.assertEqual(
            self.pointer_word("structured_file").value,
            FILE_ADDRESS,
        )
        self.assertEqual(
            self.pointer_word("structured_function").value,
            FUNCTION_ADDRESS,
        )
        self.assertEqual(self.word("structured_line").value, 221)
        self.assertEqual(
            self.pointer_word("structured_message").value,
            MESSAGE_ADDRESS,
        )
        self.assertEqual(self.word("trace_count").value, 1)
        self.assertEqual(self.word("trace_mask").value, 0x04000000)
        self.assertEqual(
            self.pointer_word("trace_format").value,
            TRACE_ADDRESS,
        )
        self.assertEqual(
            self.pointer_word("trace_argument").value,
            TRACE_ADDRESS,
        )

        for levels, kinds in (
            (
                (0, 1),
                [EVENT_LEVEL, EVENT_LEVEL, EVENT_TRACE],
            ),
            (
                (0, 0, 4),
                [EVENT_LEVEL, EVENT_LEVEL, EVENT_LEVEL, EVENT_TRACE],
            ),
            (
                (0, 0, 0),
                [EVENT_LEVEL, EVENT_LEVEL, EVENT_LEVEL],
            ),
        ):
            with self.subTest(levels=levels):
                self.reset_fixture()
                self.set_levels(*levels)
                self.assertEqual(self.set_time(ctypes.byref(invalid)), 1)
                self.assertEqual(
                    [event[0] for event in self.events()],
                    kinds,
                )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "52bd836b8b62cc2a293b445098de6850f419890046a2cd78686fd8a6f503258f",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "bd1b96f4bf41ca57c1e8f7447478a041855adec47801bdbb3f4afa47f486c908",
        )


if __name__ == "__main__":
    unittest.main()
