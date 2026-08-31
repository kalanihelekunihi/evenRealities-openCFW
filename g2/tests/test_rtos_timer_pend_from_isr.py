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
SOURCE = COMPONENT_ROOT / "rtos_timer_pend_from_isr.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_pend_from_isr_host.c"
)


class RtosTimerPendFromIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_pend_from_isr.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_pend_from_isr.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_pend_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_queue = cls.loaded.open_cfw_test_rtos_timer_pend_set_queue
        cls.set_queue.argtypes = [ctypes.c_size_t]
        cls.set_queue.restype = None
        cls.set_send_result = (
            cls.loaded.open_cfw_test_rtos_timer_pend_set_send_result
        )
        cls.set_send_result.argtypes = [ctypes.c_int]
        cls.set_send_result.restype = None
        cls.pend = cls.loaded.open_cfw_test_rtos_timer_pend_call
        cls.pend.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
        ]
        cls.pend.restype = ctypes.c_int
        cls.callback_type = ctypes.CFUNCTYPE(
            None,
            ctypes.c_void_p,
            ctypes.c_uint,
        )
        cls.callback = cls.callback_type(lambda _parameter, _value: None)
        cls.callback_address = ctypes.cast(
            cls.callback,
            ctypes.c_void_p,
        ).value

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_pend_{suffix}",
        )

    @classmethod
    def integer(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_pend_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_pend_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        values = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_pend_events",
        )
        return list(values)[:count]

    def submit(
        self,
        *,
        function: int | None = None,
        parameter: int | None = 0x2345,
        value: int = 0x6789,
        woken: ctypes.c_int | None = None,
    ) -> int:
        function_pointer = (
            self.callback_address if function is None else function
        )
        woken_pointer = None if woken is None else ctypes.byref(woken)
        return self.pend(
            function_pointer,
            parameter,
            value,
            woken_pointer,
        )

    def test_exact_four_word_daemon_message_is_forwarded(self) -> None:
        self.submit()
        self.assertEqual(self.integer("last_command").value, -2)
        self.assertEqual(
            self.uintptr("last_function").value,
            self.callback_address,
        )
        self.assertEqual(self.uintptr("last_parameter").value, 0x2345)
        self.assertEqual(self.uint("last_value").value, 0x6789)

    def test_null_callback_and_parameter_are_forwarded_without_guard(
        self,
    ) -> None:
        self.submit(function=0, parameter=None)
        self.assertEqual(self.uintptr("last_function").value, 0)
        self.assertEqual(self.uintptr("last_parameter").value, 0)
        self.assertEqual(self.uint("send_calls").value, 1)

    def test_parameter_value_preserves_all_32_bits(self) -> None:
        for value in (0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF):
            with self.subTest(value=value):
                self.reset_fixture()
                self.submit(value=value)
                self.assertEqual(self.uint("last_value").value, value)

    def test_queue_handle_is_read_fresh_once_before_each_send(self) -> None:
        for queue in (0, 0x1111, 0x2222):
            with self.subTest(queue=queue):
                self.reset_fixture()
                self.set_queue(queue)
                self.submit()
                self.assertEqual(self.uintptr("last_queue").value, queue)
                self.assertEqual(self.uint("queue_reads").value, 1)
                self.assertEqual(self.events(), [10, 20])

    def test_queue_send_result_is_returned_unchanged(self) -> None:
        for result in (-0x80000000, -7, 0, 1, 0x7FFFFFFF):
            with self.subTest(result=result):
                self.reset_fixture()
                self.set_send_result(result)
                self.assertEqual(self.submit(), result)

    def test_woken_pointer_and_copy_position_are_forwarded_exactly(
        self,
    ) -> None:
        woken = ctypes.c_int(0x12345678)
        self.submit(woken=woken)
        self.assertEqual(
            self.uintptr("last_woken").value,
            ctypes.addressof(woken),
        )
        self.assertEqual(self.uint("last_copy_position").value, 0)
        self.reset_fixture()
        self.submit(woken=None)
        self.assertEqual(self.uintptr("last_woken").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0b50b8d5a4f48c3c8008aa5e2422d3de9c517b04ac82b2b96c78f565c16e78e9",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "d0bcbc594ed2a9b90c316d331fe93e9491d2be2a8f986be26d3d23cd50eed728",
        )


if __name__ == "__main__":
    unittest.main()
