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
SOURCE = COMPONENT_ROOT / "rtos_timer_get_context.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_get_context_host.c"
)


class RtosTimerGetContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_get_context.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_get_context.so"
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
            cls.loaded.open_cfw_test_rtos_timer_get_context_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_result = (
            cls.loaded.open_cfw_test_rtos_timer_get_context_set_result
        )
        cls.set_result.argtypes = [ctypes.c_size_t]
        cls.set_result.restype = None
        cls.timer_object = (ctypes.c_ubyte * 44).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_get_context_object",
        )
        cls.get_context = cls.loaded.open_cfw_rtos_timer_get_context
        cls.get_context.argtypes = [ctypes.c_void_p]
        cls.get_context.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_get_context_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_get_context_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_get_context_{suffix}",
        )
        return list(values)

    def query(self, context: int) -> int | None:
        self.set_result(context)
        return self.get_context(ctypes.addressof(self.timer_object))

    def test_null_context_is_returned_unchanged(self) -> None:
        self.assertIsNone(self.query(0))

    def test_nonnull_context_identity_is_returned_without_normalization(
        self,
    ) -> None:
        for context in (1, 2, 0x1234, 0x12345678):
            with self.subTest(context=context):
                self.reset_fixture()
                self.assertEqual(self.query(context), context)

    def test_context_is_read_once_between_critical_entry_and_exit(self) -> None:
        self.assertEqual(self.query(0x1234), 0x1234)
        count = self.uint("event_count").value
        self.assertEqual(self.array("events", 8)[:count], [10, 20, 30])
        self.assertEqual(self.uint("context_reads").value, 1)
        self.assertEqual(self.uint("enter_calls").value, 1)
        self.assertEqual(self.uint("exit_calls").value, 1)

    def test_every_context_side_effect_occurs_inside_critical_section(
        self,
    ) -> None:
        self.query(0x5678)
        self.assertEqual(self.array("event_depths", 8)[:3], [1, 1, 1])
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_exact_timer_identity_is_forwarded_to_the_context_read(
        self,
    ) -> None:
        timer_address = ctypes.addressof(self.timer_object)
        self.query(0x9ABC)
        self.assertEqual(self.uintptr("last_timer").value, timer_address)

    def test_null_timer_fail_stops_before_critical_entry_or_context_read(
        self,
    ) -> None:
        self.assertIsNone(self.get_context(None))
        self.assertEqual(self.array("events", 8)[:1], [40])
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("enter_calls").value, 0)
        self.assertEqual(self.uint("context_reads").value, 0)
        self.assertEqual(self.uint("exit_calls").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "e620bf88641d9d4bcb74857b535cb32d6db0522fa139535fa0c57a6599031ccc",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "7130cae3ae777a4f96754e260bd46f075c2681179db4a6ef93cf97170cf606b1",
        )


if __name__ == "__main__":
    unittest.main()
