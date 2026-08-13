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
SOURCE = COMPONENT_ROOT / "rtos_timer_is_active.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_is_active_host.c"
)


class RtosTimerIsActiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_is_active.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_is_active.so"
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
            cls.loaded.open_cfw_test_rtos_timer_is_active_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_status = (
            cls.loaded.open_cfw_test_rtos_timer_is_active_set_status
        )
        cls.set_status.argtypes = [ctypes.c_uint]
        cls.set_status.restype = None
        cls.timer_object = (ctypes.c_ubyte * 44).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_is_active_object",
        )
        cls.is_active = cls.loaded.open_cfw_rtos_timer_is_active
        cls.is_active.argtypes = [ctypes.c_void_p]
        cls.is_active.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_is_active_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_is_active_{suffix}",
        )
        return list(values)

    def query(self, status: int) -> int:
        self.set_status(status)
        return self.is_active(ctypes.addressof(self.timer_object))

    def test_clear_active_bit_returns_normalized_zero(self) -> None:
        for status in (0x00, 0x02, 0x04, 0x7E, 0xFE):
            with self.subTest(status=status):
                self.reset_fixture()
                self.assertEqual(self.query(status), 0)

    def test_set_active_bit_returns_normalized_one(self) -> None:
        for status in (0x01, 0x03, 0x05, 0x7F, 0xFF):
            with self.subTest(status=status):
                self.reset_fixture()
                self.assertEqual(self.query(status), 1)

    def test_status_is_read_once_between_critical_entry_and_exit(self) -> None:
        self.assertEqual(self.query(0xA5), 1)
        count = self.uint("event_count").value
        self.assertEqual(self.array("events", 8)[:count], [10, 20, 30])
        self.assertEqual(self.uint("status_reads").value, 1)
        self.assertEqual(self.uint("enter_calls").value, 1)
        self.assertEqual(self.uint("exit_calls").value, 1)

    def test_every_status_side_effect_occurs_inside_critical_section(
        self,
    ) -> None:
        self.query(0x20)
        self.assertEqual(self.array("event_depths", 8)[:3], [1, 1, 1])
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_nonactive_status_bits_do_not_affect_the_result(self) -> None:
        for upper_bits in (0x00, 0x02, 0x54, 0x80, 0xFE):
            with self.subTest(upper_bits=upper_bits):
                self.reset_fixture()
                self.assertEqual(self.query(upper_bits), 0)
                self.reset_fixture()
                self.assertEqual(self.query(upper_bits | 1), 1)

    def test_null_timer_fail_stops_before_critical_entry_or_status_read(
        self,
    ) -> None:
        self.assertEqual(self.is_active(None), 0)
        self.assertEqual(self.array("events", 8)[:1], [40])
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("enter_calls").value, 0)
        self.assertEqual(self.uint("status_reads").value, 0)
        self.assertEqual(self.uint("exit_calls").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "f0e20d1e42d9177e553ae3c892b39eb8180bc01707ab4a985563efc2fe373aaa",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "175191ca1db26be6b1c00604511ea3d6a61e61700521fe80bdfc2449a9c401a2",
        )


if __name__ == "__main__":
    unittest.main()
