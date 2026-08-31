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
SOURCE = COMPONENT_ROOT / "rtos_timer_sample.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_sample_host.c"


class RtosTimerSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_sample.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_sample.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_sample_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.sample = cls.loaded.open_cfw_test_rtos_timer_sample_run
        cls.sample.argtypes = [ctypes.POINTER(ctypes.c_uint)]
        cls.sample.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_sample_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        values = (ctypes.c_uint * 16).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_sample_events",
        )
        return list(values)[:count]

    def run_sample(
        self,
        *,
        time_now: int,
        last_tick: int,
        initial_switched: int = 0xA5A5A5A5,
    ) -> tuple[int, int]:
        self.uint("time_now").value = time_now
        self.uint("last_tick").value = last_tick
        switched = ctypes.c_uint(initial_switched)
        result = self.sample(ctypes.byref(switched))
        return result, switched.value

    def test_equal_tick_does_not_switch_lists(self) -> None:
        self.assertEqual(
            self.run_sample(time_now=77, last_tick=77),
            (77, 0),
        )
        self.assertEqual(self.uint("switch_calls").value, 0)
        self.assertEqual(self.uint("last_tick").value, 77)

    def test_greater_tick_does_not_switch_lists(self) -> None:
        self.assertEqual(
            self.run_sample(time_now=78, last_tick=77),
            (78, 0),
        )
        self.assertEqual(self.events(), [10, 20, 40])

    def test_lower_tick_switches_lists_before_publishing_one(self) -> None:
        self.assertEqual(
            self.run_sample(time_now=3, last_tick=0xFFFFFFFE),
            (3, 1),
        )
        self.assertEqual(self.uint("switch_calls").value, 1)
        self.assertEqual(self.events(), [10, 20, 30, 40])

    def test_comparison_is_unsigned_across_high_bit(self) -> None:
        self.assertEqual(
            self.run_sample(time_now=0x80000000, last_tick=1),
            (0x80000000, 0),
        )
        self.reset_fixture()
        self.assertEqual(
            self.run_sample(time_now=1, last_tick=0x80000000),
            (1, 1),
        )

    def test_output_is_normalized_and_last_tick_is_always_updated(self) -> None:
        for now, previous, expected in (
            (0, 0, 0),
            (0, 1, 1),
            (0xFFFFFFFF, 0xFFFFFFFF, 0),
        ):
            with self.subTest(now=now, previous=previous):
                self.reset_fixture()
                self.assertEqual(
                    self.run_sample(
                        time_now=now,
                        last_tick=previous,
                        initial_switched=0xFFFFFFFF,
                    ),
                    (now, expected),
                )
                self.assertEqual(self.uint("last_tick").value, now)
                self.assertEqual(self.uint("last_tick_writes").value, 1)

    def test_tick_and_last_tick_are_each_sampled_once(self) -> None:
        self.run_sample(time_now=4, last_tick=9)
        self.assertEqual(self.uint("tick_reads").value, 1)
        self.assertEqual(self.uint("last_tick_reads").value, 1)
        self.assertEqual(self.uint("last_tick_writes").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ac37a26ca98b58c0b85001628241f96aa117923850d2848b2fe90430fccf2bbe",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "467e3abd422ae5c55b30ea96662be42b1526bec218dbf75396870a6c9c846871",
        )


if __name__ == "__main__":
    unittest.main()
