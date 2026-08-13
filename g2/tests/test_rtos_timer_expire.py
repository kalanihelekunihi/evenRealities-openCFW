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
SOURCE = COMPONENT_ROOT / "rtos_timer_expire.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_expire_host.c"


class RtosTimerExpireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_expire.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_expire.so"
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
            cls.loaded.open_cfw_test_rtos_timer_expire_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.expire = cls.loaded.open_cfw_rtos_timer_expire
        cls.expire.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.expire.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_expire_{suffix}",
        )

    @classmethod
    def byte(cls, suffix: str) -> ctypes.c_ubyte:
        return ctypes.c_ubyte.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_expire_{suffix}",
        )

    @classmethod
    def pointer(cls, suffix: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_expire_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        values = (ctypes.c_uint * 16).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_expire_events",
        )
        count = cls.uint("event_count").value
        return list(values)[:count]

    @classmethod
    def timer_address(cls) -> int:
        timer = (ctypes.c_ubyte * 64).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_expire_object",
        )
        return ctypes.addressof(timer)

    def test_periodic_timer_is_reloaded_then_called_back(self) -> None:
        timer = self.timer_address()
        self.byte("status").value = 0xE5
        self.expire(0x12345678, 0x9ABCDEF0)
        self.assertEqual(self.events(), [10, 20, 30, 40, 60])
        self.assertEqual(self.uint("timer_select_calls").value, 1)
        self.assertEqual(self.uint("remove_calls").value, 1)
        self.assertEqual(self.uint("status_reads").value, 1)
        self.assertEqual(self.uint("status_writes").value, 0)
        self.assertEqual(self.uint("reload_calls").value, 1)
        self.assertEqual(self.uint("callback_calls").value, 1)
        self.assertEqual(self.pointer("reload_timer").value, timer)
        self.assertEqual(self.pointer("callback_timer").value, timer)
        self.assertEqual(self.uint("expired_time").value, 0x12345678)
        self.assertEqual(self.uint("time_now").value, 0x9ABCDEF0)
        self.assertEqual(self.byte("status").value, 0xE5)

    def test_one_shot_timer_clears_only_active_bit_before_callback(self) -> None:
        self.byte("status").value = 0xAB
        self.expire(17, 23)
        self.assertEqual(self.events(), [10, 20, 30, 30, 50, 60])
        self.assertEqual(self.uint("reload_calls").value, 0)
        self.assertEqual(self.uint("status_reads").value, 2)
        self.assertEqual(self.uint("status_writes").value, 1)
        self.assertEqual(self.byte("written_status").value, 0xAA)
        self.assertEqual(self.byte("status").value, 0xAA)
        self.assertEqual(self.byte("callback_status").value, 0xAA)
        self.assertEqual(self.uint("callback_calls").value, 1)

    def test_one_shot_clear_uses_a_fresh_status_read(self) -> None:
        self.byte("status").value = 0x01
        self.uint("status_mutate_after_read").value = 0
        self.uint("mutated_status").value = 0xF3
        self.expire(1, 2)
        self.assertEqual(self.uint("status_reads").value, 2)
        self.assertEqual(self.byte("written_status").value, 0xF2)
        self.assertEqual(self.byte("callback_status").value, 0xF2)

    def test_inactive_one_shot_status_is_written_without_other_changes(
        self,
    ) -> None:
        self.byte("status").value = 0xA2
        self.expire(0, 0)
        self.assertEqual(self.byte("written_status").value, 0xA2)
        self.assertEqual(self.byte("callback_status").value, 0xA2)

    def test_list_item_at_timer_plus_four_is_removed(self) -> None:
        timer = self.timer_address()
        self.expire(3, 4)
        self.assertEqual(self.pointer("removed_item").value, timer + 4)
        self.assertEqual(self.uint("timer_select_calls").value, 1)

    def test_remove_return_value_is_ignored(self) -> None:
        for result in (0, 1, 0xFFFFFFFF):
            with self.subTest(result=result):
                self.reset_fixture()
                self.uint("remove_result").value = result
                self.byte("status").value = 0x04
                self.expire(5, 6)
                self.assertEqual(self.uint("reload_calls").value, 1)
                self.assertEqual(self.uint("callback_calls").value, 1)

    def test_periodicity_is_controlled_by_status_bit_two(self) -> None:
        for status, expected_reload in (
            (0x00, 0),
            (0x01, 0),
            (0x02, 0),
            (0x04, 1),
            (0x05, 1),
            (0xFF, 1),
        ):
            with self.subTest(status=status):
                self.reset_fixture()
                self.byte("status").value = status
                self.expire(7, 8)
                self.assertEqual(
                    self.uint("reload_calls").value,
                    expected_reload,
                )
                self.assertEqual(self.uint("callback_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "94e1f1361cda2c5bfed2323719a9b19bb9478f53211238cd03cfd7b917edffbd",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "31e36384949f65d0a79bcb3018885e908bff2755952461e47d36af2536af2f64",
        )


if __name__ == "__main__":
    unittest.main()
