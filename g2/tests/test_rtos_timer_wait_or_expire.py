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
SOURCE = COMPONENT_ROOT / "rtos_timer_wait_or_expire.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_wait_or_expire_host.c"
)


class RtosTimerWaitOrExpireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_wait_or_expire.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_wait_or_expire.so"
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
        cls.reset_fixture = (
            cls.loaded.open_cfw_test_rtos_timer_wait_or_expire_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.process = cls.loaded.open_cfw_rtos_timer_wait_or_expire
        cls.process.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.process.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_wait_or_expire_{suffix}",
        )

    @classmethod
    def pointer(cls, suffix: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_wait_or_expire_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        values = (ctypes.c_uint * 24).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_wait_or_expire_events",
        )
        return list(values)[:cls.uint("event_count").value]

    def configure(
        self,
        *,
        time_now: int,
        switched: int = 0,
        resume_result: int = 1,
        overflow_empty: int = 0,
        queue: int = 0x12345678,
    ) -> None:
        self.uint("time_now").value = time_now
        self.uint("lists_switched").value = switched
        self.uint("resume_result").value = resume_result
        self.uint("overflow_empty").value = overflow_empty
        self.pointer("queue").value = queue

    def test_due_nonempty_timer_resumes_then_expires(self) -> None:
        self.configure(time_now=100, resume_result=0)
        self.process(100, 0)
        self.assertEqual(self.events(), [10, 20, 50, 60])
        self.assertEqual(self.uint("resume_calls").value, 1)
        self.assertEqual(self.uint("expire_calls").value, 1)
        self.assertEqual(self.uint("expired_time").value, 100)
        self.assertEqual(self.uint("expired_time_now").value, 100)
        self.assertEqual(self.uint("wait_calls").value, 0)
        self.assertEqual(self.uint("yield_calls").value, 0)

    def test_future_nonempty_timer_blocks_for_unsigned_delta(self) -> None:
        self.configure(time_now=100, queue=0xABCDEF01)
        self.process(135, 0)
        self.assertEqual(self.events(), [10, 20, 35, 40, 50])
        self.assertEqual(self.pointer("wait_queue").value, 0xABCDEF01)
        self.assertEqual(self.uint("wait_delay").value, 35)
        self.assertEqual(self.uint("wait_indefinitely").value, 0)
        self.assertEqual(self.uint("overflow_calls").value, 0)
        self.assertEqual(self.uint("expire_calls").value, 0)

    def test_empty_active_list_recomputes_overflow_emptiness(self) -> None:
        for overflow_empty in (0, 1, 0xFFFFFFFF):
            with self.subTest(overflow_empty=overflow_empty):
                self.reset_fixture()
                self.configure(
                    time_now=20,
                    overflow_empty=overflow_empty,
                )
                self.process(50, 1)
                self.assertEqual(
                    self.events(),
                    [10, 20, 30, 35, 40, 50],
                )
                self.assertEqual(self.uint("overflow_calls").value, 1)
                self.assertEqual(
                    self.uint("wait_indefinitely").value,
                    int(overflow_empty != 0),
                )

    def test_timer_list_switch_only_resumes_scheduler(self) -> None:
        self.configure(
            time_now=0xFFFFFFFF,
            switched=7,
            resume_result=0,
        )
        self.process(0, 0)
        self.assertEqual(self.events(), [10, 20, 50])
        self.assertEqual(self.uint("resume_calls").value, 1)
        self.assertEqual(self.uint("wait_calls").value, 0)
        self.assertEqual(self.uint("expire_calls").value, 0)
        self.assertEqual(self.uint("yield_calls").value, 0)

    def test_zero_resume_result_yields_only_after_queue_wait(self) -> None:
        self.configure(time_now=10, resume_result=0)
        self.process(20, 0)
        self.assertEqual(self.events(), [10, 20, 35, 40, 50, 70])
        self.assertEqual(self.uint("yield_calls").value, 1)

        self.reset_fixture()
        self.configure(time_now=10, resume_result=9)
        self.process(20, 0)
        self.assertEqual(self.events(), [10, 20, 35, 40, 50])
        self.assertEqual(self.uint("yield_calls").value, 0)

    def test_unsigned_comparison_and_delay_wrap_match_stock(self) -> None:
        self.configure(time_now=0xFFFFFFFF)
        self.process(0, 0)
        self.assertEqual(self.uint("expire_calls").value, 1)

        self.reset_fixture()
        self.configure(time_now=0x10)
        self.process(0xFFFFFFF0, 0)
        self.assertEqual(self.uint("expire_calls").value, 0)
        self.assertEqual(self.uint("wait_delay").value, 0xFFFFFFE0)

    def test_any_nonzero_active_empty_or_switched_value_is_true(self) -> None:
        self.configure(time_now=50, overflow_empty=1)
        self.process(1, 0x80000000)
        self.assertEqual(self.uint("expire_calls").value, 0)
        self.assertEqual(self.uint("overflow_calls").value, 1)

        self.reset_fixture()
        self.configure(time_now=50, switched=0xFFFFFFFF)
        self.process(1, 0)
        self.assertEqual(self.events(), [10, 20, 50])

    def test_scheduler_is_suspended_before_sampling_every_path(self) -> None:
        for next_expiry, active_empty, time_now, switched in (
            (10, 0, 10, 0),
            (20, 0, 10, 0),
            (20, 1, 10, 0),
            (20, 0, 10, 1),
        ):
            with self.subTest(
                next_expiry=next_expiry,
                active_empty=active_empty,
                switched=switched,
            ):
                self.reset_fixture()
                self.configure(time_now=time_now, switched=switched)
                self.process(next_expiry, active_empty)
                self.assertEqual(self.events()[:2], [10, 20])
                self.assertEqual(self.uint("suspend_calls").value, 1)
                self.assertEqual(self.uint("sample_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ada5fba0b94f32690e51a5e8f46c040738b4f790165e66e5bd5fbb26570eee7c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ddd49faa7399493081146ebb785431b233fd7bb12ea27c0e73ec113e87c13294",
        )


if __name__ == "__main__":
    unittest.main()
