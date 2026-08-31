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
SOURCE = COMPONENT_ROOT / "rtos_timer_reload.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_reload_host.c"


class RtosTimerReloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_reload.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_reload.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_reload_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.reload = cls.loaded.open_cfw_rtos_timer_reload
        cls.reload.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
        cls.reload.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_reload_{suffix}",
        )

    @classmethod
    def uint_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_reload_{suffix}",
        )

    @classmethod
    def pointer_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_void_p]:
        return (ctypes.c_void_p * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_reload_{suffix}",
        )

    def configure(
        self,
        *,
        period: int,
        insert_results: tuple[int, ...],
    ) -> None:
        self.uint("period").value = period
        results = self.uint_array("insert_results", 16)
        for index, result in enumerate(insert_results):
            results[index] = result
        self.uint("insert_result_count").value = len(insert_results)

    def run_reload(
        self,
        *,
        timer: int = 0x12345678,
        expired_time: int = 100,
        time_now: int = 200,
    ) -> None:
        self.reload(timer, expired_time, time_now)

    def test_first_insert_schedules_without_callback(self) -> None:
        self.configure(period=7, insert_results=(0,))
        self.run_reload()
        self.assertEqual(self.uint("period_reads").value, 1)
        self.assertEqual(self.uint("insert_calls").value, 1)
        self.assertEqual(self.uint("callback_calls").value, 0)
        self.assertEqual(list(self.uint_array("events", 48))[:2], [10, 20])
        self.assertEqual(self.uint_array("next_expiry", 16)[0], 107)
        self.assertEqual(self.uint_array("time_now", 16)[0], 200)
        self.assertEqual(self.uint_array("expired_time", 16)[0], 100)

    def test_expired_deadline_callbacks_then_retries_next_period(self) -> None:
        self.configure(period=7, insert_results=(1, 0))
        self.run_reload()
        self.assertEqual(
            list(self.uint_array("events", 48))[:6],
            [10, 20, 10, 30, 10, 20],
        )
        self.assertEqual(
            list(self.uint_array("next_expiry", 16))[:2],
            [107, 114],
        )
        self.assertEqual(
            list(self.uint_array("expired_time", 16))[:2],
            [100, 107],
        )
        self.assertEqual(self.uint("callback_calls").value, 1)

    def test_multiple_catchups_use_unsigned_32_bit_arithmetic(self) -> None:
        self.configure(period=0x20, insert_results=(1, 1, 0))
        self.run_reload(expired_time=0xFFFFFFF0, time_now=0x12)
        self.assertEqual(
            list(self.uint_array("next_expiry", 16))[:3],
            [0x10, 0x30, 0x50],
        )
        self.assertEqual(
            list(self.uint_array("expired_time", 16))[:3],
            [0xFFFFFFF0, 0x10, 0x30],
        )
        self.assertEqual(
            list(self.uint_array("time_now", 16))[:3],
            [0x12, 0x12, 0x12],
        )
        self.assertEqual(self.uint("callback_calls").value, 2)

    def test_period_is_reread_after_insert_before_advancing_expiry(self) -> None:
        self.configure(period=7, insert_results=(1, 0))
        self.uint("insert_mutate_call").value = 0
        self.uint("insert_period_value").value = 11
        self.run_reload()
        self.assertEqual(
            list(self.uint_array("next_expiry", 16))[:2],
            [107, 122],
        )
        self.assertEqual(
            list(self.uint_array("expired_time", 16))[:2],
            [100, 111],
        )

    def test_callback_period_change_affects_the_following_retry(self) -> None:
        self.configure(period=5, insert_results=(1, 0))
        self.uint("callback_mutates_period").value = 1
        self.uint("callback_period_value").value = 9
        self.run_reload()
        self.assertEqual(
            list(self.uint_array("next_expiry", 16))[:2],
            [105, 114],
        )
        self.assertEqual(
            list(self.uint_array("expired_time", 16))[:2],
            [100, 105],
        )

    def test_any_nonzero_insert_result_is_treated_as_expired(self) -> None:
        self.configure(period=1, insert_results=(0xFFFFFFFF, 2, 0))
        self.run_reload()
        self.assertEqual(self.uint("callback_calls").value, 2)
        self.assertEqual(self.uint("insert_calls").value, 3)

    def test_timer_identity_is_forwarded_to_insert_and_callback(self) -> None:
        timer = 0x123456789ABCDEF0
        self.configure(period=3, insert_results=(1, 0))
        self.run_reload(timer=timer)
        self.assertEqual(
            list(self.pointer_array("insert_timer", 16))[:2],
            [timer, timer],
        )
        self.assertEqual(
            list(self.pointer_array("callback_timer", 16))[:1],
            [timer],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "d80337315fa2eaab25732faea3470b53adb80ccf0bb068f81b7c988d4bfa360e",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "3c31afc0d882e27f83f0cd5edffb22040d636a66ccb95791600c9645896b121d",
        )


if __name__ == "__main__":
    unittest.main()
