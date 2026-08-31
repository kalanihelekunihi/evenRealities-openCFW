from __future__ import annotations

import os

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "rtos_timer_insert.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_insert_host.c"


class RtosTimerInsertTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_insert.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_insert.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_insert_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.insert = cls.loaded.open_cfw_test_rtos_timer_insert_run
        cls.insert.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.insert.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_insert_{suffix}",
        )

    @classmethod
    def timer(cls) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * 11).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_insert_timer",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        values = (ctypes.c_uint * 16).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_insert_events",
        )
        return list(values)[:count]

    @classmethod
    def pointer(cls, suffix: str) -> int:
        return ctypes.addressof(
            ctypes.c_uint.in_dll(
                cls.loaded,
                f"open_cfw_test_rtos_timer_insert_{suffix}",
            )
        )

    @classmethod
    def pointer_array(
        cls,
        suffix: str,
    ) -> ctypes.Array[ctypes.c_void_p]:
        return (ctypes.c_void_p * 4).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_insert_{suffix}",
        )

    def test_future_deadline_is_inserted_into_active_list(self) -> None:
        result = self.insert(20, 10, 5)
        self.assertEqual(result, 0)
        self.assertEqual(self.uint("active_list_reads").value, 1)
        self.assertEqual(self.uint("overflow_list_reads").value, 0)
        self.assertEqual(self.events(), [10, 20, 40, 60])
        self.assertEqual(
            self.pointer_array("lists")[0],
            self.pointer("active_list_tag"),
        )

    def test_wrapped_previous_deadline_can_still_use_active_list(self) -> None:
        self.assertEqual(
            self.insert(10, 3, 0xFFFFFFF0),
            0,
        )
        self.assertEqual(self.uint("active_list_reads").value, 1)

    def test_future_window_containing_previous_expiry_is_expired(self) -> None:
        self.assertEqual(self.insert(10, 3, 5), 1)
        self.assertEqual(self.uint("list_calls").value, 0)
        self.assertEqual(self.uint("period_reads").value, 0)
        self.assertEqual(self.events(), [10, 20])

    def test_recent_due_deadline_is_inserted_into_overflow_list(self) -> None:
        timer = self.timer()
        timer[6] = 10
        self.assertEqual(self.insert(80, 100, 95), 0)
        self.assertEqual(self.uint("active_list_reads").value, 0)
        self.assertEqual(self.uint("overflow_list_reads").value, 1)
        self.assertEqual(self.events(), [10, 20, 30, 50, 60])
        self.assertEqual(
            self.pointer_array("lists")[0],
            self.pointer("overflow_list_tag"),
        )

    def test_elapsed_period_or_more_is_expired(self) -> None:
        timer = self.timer()
        for period, expected in ((6, 0), (5, 1), (4, 1)):
            with self.subTest(period=period):
                self.reset_fixture()
                timer[6] = period
                self.assertEqual(
                    self.insert(2, 3, 0xFFFFFFFE),
                    expected,
                )
                self.assertEqual(
                    self.uint("overflow_list_reads").value,
                    1 if expected == 0 else 0,
                )

    def test_comparison_boundaries_match_stock_unsigned_policy(self) -> None:
        timer = self.timer()
        cases = (
            (10, 10, 10, 1),
            (11, 10, 10, 0),
            (11, 10, 11, 1),
            (11, 10, 5, 0),
        )
        for next_expiry, time_now, previous, expected in cases:
            with self.subTest(
                next_expiry=next_expiry,
                time_now=time_now,
                previous=previous,
            ):
                self.reset_fixture()
                timer[6] = 0
                self.assertEqual(
                    self.insert(next_expiry, time_now, previous),
                    expected,
                )

    def test_item_fields_and_list_item_identity_are_always_exact(self) -> None:
        timer = self.timer()
        timer_address = ctypes.addressof(timer)
        self.assertEqual(
            self.insert(0xFEDCBA98, 1, 0),
            0,
        )
        self.assertEqual(timer[1], 0xFEDCBA98)
        self.assertEqual(timer[4], timer_address & 0xFFFFFFFF)
        self.assertEqual(
            self.pointer_array("items")[0],
            timer_address + 4,
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "d0c78173a675d572ea1ebf197e947e8ce3c0d9dec8e7a0b22f425eb43cbace22",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "657d35826ace0fb4aa5b2be2e379b82713ba01aee7293ee91539ceea8ec36bc7",
        )


if __name__ == "__main__":
    unittest.main()
