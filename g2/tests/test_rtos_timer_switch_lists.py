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
SOURCE = COMPONENT_ROOT / "rtos_timer_switch_lists.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_switch_lists_host.c"
)


class RtosTimerSwitchListsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_switch_lists.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_switch_lists.so"
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

        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_switch_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.configure = cls.loaded.open_cfw_test_rtos_timer_switch_configure
        cls.configure.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.configure.restype = None
        cls.set_current = cls.loaded.open_cfw_test_rtos_timer_switch_set_current
        cls.set_current.argtypes = [ctypes.c_uint]
        cls.set_current.restype = None
        cls.set_overflow = (
            cls.loaded.open_cfw_test_rtos_timer_switch_set_overflow
        )
        cls.set_overflow.argtypes = [ctypes.c_uint]
        cls.set_overflow.restype = None
        cls.set_next_expiry = (
            cls.loaded.open_cfw_test_rtos_timer_switch_set_next_expiry
        )
        cls.set_next_expiry.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_next_expiry.restype = None
        cls.set_redirect = (
            cls.loaded.open_cfw_test_rtos_timer_switch_set_redirect
        )
        cls.set_redirect.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_redirect.restype = None
        cls.current_identity = (
            cls.loaded.open_cfw_test_rtos_timer_switch_current_identity
        )
        cls.current_identity.argtypes = []
        cls.current_identity.restype = ctypes.c_uint
        cls.overflow_identity = (
            cls.loaded.open_cfw_test_rtos_timer_switch_overflow_identity
        )
        cls.overflow_identity.argtypes = []
        cls.overflow_identity.restype = ctypes.c_uint
        cls.switch_lists = cls.loaded.open_cfw_test_rtos_timer_switch_run
        cls.switch_lists.argtypes = []
        cls.switch_lists.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_switch_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_switch_{suffix}",
        )
        return list(values)

    def events(self) -> list[int]:
        return self.array("events", 128)[:self.uint("event_count").value]

    def test_empty_current_list_swaps_exact_pointer_identities(self) -> None:
        self.set_current(0)
        self.set_overflow(1)
        self.switch_lists()
        self.assertEqual(self.current_identity(), 1)
        self.assertEqual(self.overflow_identity(), 0)
        self.assertEqual(self.uint("process_calls").value, 0)
        self.assertEqual(self.events(), [10, 30, 10, 20, 60, 70])

    def test_every_current_timer_expires_before_the_swap(self) -> None:
        self.configure(0, 3, 10)
        self.set_next_expiry(0, 20)
        self.set_next_expiry(1, 0xFFFFFFFF)
        self.switch_lists()
        self.assertEqual(self.uint("process_calls").value, 3)
        self.assertEqual(
            self.array("process_expiries", 16)[:3],
            [10, 20, 0xFFFFFFFF],
        )
        self.assertEqual(
            self.array("process_times", 16)[:3],
            [0xFFFFFFFF] * 3,
        )
        self.assertEqual(self.current_identity(), 1)
        self.assertEqual(self.overflow_identity(), 0)

    def test_current_list_is_freshly_read_after_each_expiry(self) -> None:
        self.configure(0, 1, 0x12345678)
        self.configure(2, 1, 0xABCDEF01)
        self.set_redirect(1, 2)
        self.switch_lists()
        self.assertEqual(
            self.array("process_expiries", 16)[:2],
            [0x12345678, 0xABCDEF01],
        )
        self.assertEqual(self.current_identity(), 1)
        self.assertEqual(self.overflow_identity(), 2)

    def test_empty_list_never_reads_a_head_item(self) -> None:
        self.configure(0, 0, 0xDEADBEEF)
        self.switch_lists()
        self.assertEqual(self.uint("head_reads").value, 0)
        self.assertEqual(self.uint("count_reads").value, 1)

    def test_reads_and_writes_match_stock_loop_and_swap_order(self) -> None:
        self.configure(0, 2, 1)
        self.set_next_expiry(0, 2)
        self.switch_lists()
        self.assertEqual(self.uint("current_reads").value, 6)
        self.assertEqual(self.uint("overflow_reads").value, 1)
        self.assertEqual(self.uint("count_reads").value, 3)
        self.assertEqual(self.uint("head_reads").value, 2)
        self.assertEqual(self.uint("current_writes").value, 1)
        self.assertEqual(self.uint("overflow_writes").value, 1)
        self.assertEqual(
            self.events(),
            [
                10, 30, 10, 40, 50,
                10, 30, 10, 40, 50,
                10, 30, 10, 20, 60, 70,
            ],
        )

    def test_head_expiry_preserves_all_32_bits(self) -> None:
        for expiry in (0, 1, 0x80000000, 0xFFFFFFFF):
            with self.subTest(expiry=expiry):
                self.reset_fixture()
                self.configure(0, 1, expiry)
                self.switch_lists()
                self.assertEqual(
                    self.array("process_expiries", 16)[0],
                    expiry,
                )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "aa333cd863267000b7f71cbf4c950cae1412728cce0c9b48bb9894ee077668c9",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ec5baf5f3e0b4eb244b2b9ae9ec415d5631dd53ffe8f28a3d1baca422a985ac4",
        )


if __name__ == "__main__":
    unittest.main()
