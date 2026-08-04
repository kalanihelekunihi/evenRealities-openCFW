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
SOURCE = COMPONENT_ROOT / "tracepoint_defer.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "tracepoint_defer_host.c"
UINT_MASK = (1 << 32) - 1


class TracepointDeferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tracepoint_defer.dylib"
            if sys.platform == "darwin"
            else "tracepoint_defer.so"
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

        cls.dispatch = cls.loaded.open_cfw_tracepoint_defer_dispatch
        cls.dispatch.argtypes = []
        cls.dispatch.restype = None
        cls.callback = (
            cls.loaded.open_cfw_tracepoint_defer_timer_callback
        )
        cls.callback.argtypes = [ctypes.c_void_p]
        cls.callback.restype = None
        cls.begin = cls.loaded.open_cfw_tracepoint_defer_begin
        cls.begin.argtypes = []
        cls.begin.restype = None
        cls.retry = cls.loaded.open_cfw_tracepoint_capture_retry
        cls.retry.argtypes = []
        cls.retry.restype = None

        cls.trace = (
            ctypes.c_uint * 16
        ).in_dll(cls.loaded, "open_cfw_test_tracepoint_trace")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def word(cls, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(cls.loaded, name)

    @classmethod
    def signed_word(cls, name: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(cls.loaded, name)

    @classmethod
    def pointer(cls, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(cls.loaded, name)

    @classmethod
    def uintptr(cls, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(cls.loaded, name)

    def reset(
        self,
        *,
        should_defer: int,
        capture_result: int = 0,
        retry_count: int = 0,
        timer_handle: int = 0x12345678,
    ) -> None:
        self.word("open_cfw_test_tracepoint_should_defer").value = (
            should_defer & UINT_MASK
        )
        self.word("open_cfw_test_tracepoint_capture_result").value = (
            capture_result & UINT_MASK
        )
        self.word("open_cfw_test_tracepoint_event_result").value = (
            0xE001E001
        )
        self.word("open_cfw_test_tracepoint_timer_result").value = (
            0x70017001
        )
        self.pointer("open_cfw_test_tracepoint_timer_handle").value = (
            timer_handle
        )
        self.signed_word(
            "open_cfw_test_tracepoint_retry_count"
        ).value = retry_count

        for name in (
            "open_cfw_test_tracepoint_query_calls",
            "open_cfw_test_tracepoint_event_calls",
            "open_cfw_test_tracepoint_capture_calls",
            "open_cfw_test_tracepoint_timer_calls",
            "open_cfw_test_tracepoint_query_observed_retry_count",
            "open_cfw_test_tracepoint_capture_observed_retry_count",
            "open_cfw_test_tracepoint_timer_observed_retry_count",
            "open_cfw_test_tracepoint_timer_command",
            "open_cfw_test_tracepoint_timer_value",
            "open_cfw_test_tracepoint_timer_wait_ticks",
            "open_cfw_test_tracepoint_trace_count",
        ):
            self.word(name).value = 0
        for name in (
            "open_cfw_test_tracepoint_timer_argument",
            "open_cfw_test_tracepoint_timer_woken_argument",
        ):
            self.uintptr(name).value = 0
        self.trace[:] = [0] * 16

    def observed_trace(self) -> list[int]:
        count = self.word(
            "open_cfw_test_tracepoint_trace_count"
        ).value
        return list(self.trace[:count])

    def assert_timer_command(
        self,
        *,
        timer_handle: int,
        value: int,
        retry_count: int,
    ) -> None:
        self.assertEqual(
            self.uintptr(
                "open_cfw_test_tracepoint_timer_argument"
            ).value,
            timer_handle,
        )
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_timer_command").value,
            4,
        )
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_timer_value").value,
            value,
        )
        self.assertEqual(
            self.uintptr(
                "open_cfw_test_tracepoint_timer_woken_argument"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_tracepoint_timer_wait_ticks"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_tracepoint_timer_observed_retry_count"
            ).value,
            retry_count & UINT_MASK,
        )

    def test_dispatch_defers_or_sets_event_in_exact_order(self) -> None:
        self.reset(should_defer=1, retry_count=7)
        self.dispatch()
        self.assertEqual(self.observed_trace(), [1, 4])
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_timer_calls").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_event_calls").value,
            0,
        )
        self.assert_timer_command(
            timer_handle=0x12345678,
            value=2000,
            retry_count=7,
        )

        self.reset(should_defer=0, retry_count=7)
        self.dispatch()
        self.assertEqual(self.observed_trace(), [1, 2])
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_timer_calls").value,
            0,
        )
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_event_calls").value,
            1,
        )

    def test_callback_ignores_callback_timer_and_uses_global_handle(
        self,
    ) -> None:
        self.reset(
            should_defer=UINT_MASK,
            retry_count=3,
            timer_handle=0xA5A5A5A5,
        )
        self.callback(ctypes.c_void_p(0xDEADBEEF))
        self.assertEqual(self.observed_trace(), [1, 4])
        self.assert_timer_command(
            timer_handle=0xA5A5A5A5,
            value=2000,
            retry_count=3,
        )

    def test_begin_requires_timer_then_clears_before_dispatch(self) -> None:
        self.reset(
            should_defer=0,
            retry_count=9,
            timer_handle=0,
        )
        self.begin()
        self.assertEqual(self.observed_trace(), [])
        self.assertEqual(
            self.signed_word(
                "open_cfw_test_tracepoint_retry_count"
            ).value,
            9,
        )

        self.reset(
            should_defer=0,
            retry_count=9,
            timer_handle=0x11112222,
        )
        self.begin()
        self.assertEqual(self.observed_trace(), [1, 2])
        self.assertEqual(
            self.word(
                "open_cfw_test_tracepoint_query_observed_retry_count"
            ).value,
            0,
        )
        self.assertEqual(
            self.signed_word(
                "open_cfw_test_tracepoint_retry_count"
            ).value,
            0,
        )

    def test_retry_deferred_path_skips_capture_and_preserves_count(
        self,
    ) -> None:
        self.reset(
            should_defer=1,
            capture_result=1,
            retry_count=6,
        )
        self.retry()
        self.assertEqual(self.observed_trace(), [1, 4])
        self.assertEqual(
            self.word("open_cfw_test_tracepoint_capture_calls").value,
            0,
        )
        self.assertEqual(
            self.signed_word(
                "open_cfw_test_tracepoint_retry_count"
            ).value,
            6,
        )
        self.assert_timer_command(
            timer_handle=0x12345678,
            value=2000,
            retry_count=6,
        )

    def test_retry_capture_failure_and_limit_do_not_rearm(self) -> None:
        for capture_result, retry_count in (
            (0, -2),
            (0, 9),
            (1, 10),
            (1, 11),
            (1, (1 << 31) - 1),
        ):
            with self.subTest(
                capture_result=capture_result,
                retry_count=retry_count,
            ):
                self.reset(
                    should_defer=0,
                    capture_result=capture_result,
                    retry_count=retry_count,
                )
                self.retry()
                self.assertEqual(self.observed_trace(), [1, 3])
                self.assertEqual(
                    self.word(
                        "open_cfw_test_tracepoint_timer_calls"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.signed_word(
                        "open_cfw_test_tracepoint_retry_count"
                    ).value,
                    retry_count,
                )

    def test_retry_success_increments_before_five_second_rearm(
        self,
    ) -> None:
        for retry_count in (-(1 << 31), -2, -1, 0, 8, 9):
            with self.subTest(retry_count=retry_count):
                self.reset(
                    should_defer=0,
                    capture_result=1,
                    retry_count=retry_count,
                )
                self.retry()
                expected = retry_count + 1
                self.assertEqual(self.observed_trace(), [1, 3, 4])
                self.assertEqual(
                    self.word(
                        "open_cfw_test_tracepoint_capture_observed_retry_count"
                    ).value,
                    retry_count & UINT_MASK,
                )
                self.assertEqual(
                    self.signed_word(
                        "open_cfw_test_tracepoint_retry_count"
                    ).value,
                    expected,
                )
                self.assert_timer_command(
                    timer_handle=0x12345678,
                    value=5000,
                    retry_count=expected,
                )

    def test_randomized_retry_model(self) -> None:
        generator = random.Random(0x0047DDAC)
        for _ in range(500):
            should_defer = generator.getrandbits(1)
            capture_result = generator.getrandbits(1)
            retry_count = ctypes.c_int(
                generator.getrandbits(32)
            ).value
            self.reset(
                should_defer=should_defer,
                capture_result=capture_result,
                retry_count=retry_count,
            )
            self.retry()

            if should_defer:
                expected_trace = [1, 4]
                expected_count = retry_count
                expected_timer_value = 2000
            elif capture_result and retry_count < 10:
                expected_trace = [1, 3, 4]
                expected_count = retry_count + 1
                expected_timer_value = 5000
            else:
                expected_trace = [1, 3]
                expected_count = retry_count
                expected_timer_value = None

            self.assertEqual(self.observed_trace(), expected_trace)
            self.assertEqual(
                self.signed_word(
                    "open_cfw_test_tracepoint_retry_count"
                ).value,
                expected_count,
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_tracepoint_timer_calls"
                ).value,
                int(expected_timer_value is not None),
            )
            if expected_timer_value is not None:
                self.assert_timer_command(
                    timer_handle=0x12345678,
                    value=expected_timer_value,
                    retry_count=expected_count,
                )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "dc4014fea7a2ae49c770caae114c6837b57ff24ea03746fd022378d86cd4b8d8",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "d4c1435f1c0189ca789e59fd7747330f28828fa1545a288bb0628697cc73b829",
        )


if __name__ == "__main__":
    unittest.main()
