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
SOURCE = COMPONENT_ROOT / "rtos_timer_command.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_command_host.c"


class RtosTimerCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_command.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_command.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_command_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.command = cls.loaded.open_cfw_rtos_timer_command
        cls.command.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_uint,
        ]
        cls.command.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_command_{suffix}",
        )

    @classmethod
    def uint_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_command_{suffix}",
        )

    @classmethod
    def pointer(cls, suffix: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_command_{suffix}",
        )

    def use_queue(self, address: int = 0x12345678) -> None:
        self.pointer("queue").value = address

    def submit(
        self,
        *,
        timer: int = 0x23456789,
        command_id: int = 4,
        optional_value: int = 0x3456789A,
        higher_priority_task_woken: ctypes.c_uint | None = None,
        ticks_to_wait: int = 0x456789AB,
    ) -> int:
        higher_pointer = (
            ctypes.byref(higher_priority_task_woken)
            if higher_priority_task_woken is not None
            else None
        )
        return self.command(
            timer,
            command_id,
            optional_value,
            higher_pointer,
            ticks_to_wait,
        )

    def test_null_timer_fail_stops_before_queue_or_kernel_access(self) -> None:
        self.use_queue()
        self.assertEqual(self.submit(timer=0), 0)
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("queue_load_calls").value, 0)
        self.assertEqual(self.uint("scheduler_calls").value, 0)
        self.assertEqual(self.uint("task_send_calls").value, 0)
        self.assertEqual(self.uint("isr_send_calls").value, 0)
        self.assertEqual(list(self.uint_array("events", 16))[:1], [40])

    def test_null_timer_queue_returns_zero_without_kernel_send(self) -> None:
        self.assertEqual(self.submit(), 0)
        self.assertEqual(self.uint("queue_load_calls").value, 1)
        self.assertEqual(self.uint("scheduler_calls").value, 0)
        self.assertEqual(self.uint("task_send_calls").value, 0)
        self.assertEqual(self.uint("isr_send_calls").value, 0)
        self.assertEqual(list(self.uint_array("events", 16))[:1], [1])

    def test_running_scheduler_forwards_wait_and_exact_message(self) -> None:
        self.use_queue()
        self.uint("task_result").value = 0x89ABCDEF
        self.assertEqual(self.submit(), 0x89ABCDEF)
        self.assertEqual(
            list(self.uint_array("events", 16))[:3],
            [1, 2, 3],
        )
        self.assertEqual(
            list(self.uint_array("message", 3)),
            [4, 0x3456789A, 0x23456789],
        )
        self.assertEqual(self.uint("ticks_to_wait").value, 0x456789AB)
        self.assertEqual(self.uint("copy_position").value, 0)
        self.assertEqual(self.pointer("observed_queue").value, 0x12345678)

    def test_nonrunning_scheduler_forces_zero_wait(self) -> None:
        self.use_queue()
        for scheduler_state in (0, 1, 3, 0xFFFFFFFF):
            with self.subTest(scheduler_state=scheduler_state):
                self.reset_fixture()
                self.use_queue()
                self.uint("scheduler_state").value = scheduler_state
                self.submit(ticks_to_wait=0xFFFFFFFF)
                self.assertEqual(self.uint("ticks_to_wait").value, 0)

    def test_signed_command_boundary_selects_task_or_isr_path(self) -> None:
        for command_id, task_calls, isr_calls in (
            (-1, 1, 0),
            (5, 1, 0),
            (6, 0, 1),
        ):
            with self.subTest(command_id=command_id):
                self.reset_fixture()
                self.use_queue()
                self.submit(command_id=command_id)
                self.assertEqual(
                    self.uint("task_send_calls").value,
                    task_calls,
                )
                self.assertEqual(
                    self.uint("isr_send_calls").value,
                    isr_calls,
                )
                self.assertEqual(
                    self.uint_array("message", 3)[0],
                    command_id & 0xFFFFFFFF,
                )

    def test_isr_path_skips_scheduler_and_forwards_wake_pointer(self) -> None:
        self.use_queue()
        self.uint("isr_result").value = 0x76543210
        higher_priority_task_woken = ctypes.c_uint(0)
        result = self.submit(
            command_id=6,
            higher_priority_task_woken=higher_priority_task_woken,
            ticks_to_wait=0xFFFFFFFF,
        )
        self.assertEqual(result, 0x76543210)
        self.assertEqual(self.uint("scheduler_calls").value, 0)
        self.assertEqual(self.uint("task_send_calls").value, 0)
        self.assertEqual(self.uint("isr_send_calls").value, 1)
        self.assertEqual(
            self.pointer("higher_priority_task_woken").value,
            ctypes.addressof(higher_priority_task_woken),
        )
        self.assertEqual(self.uint("copy_position").value, 0)
        self.assertEqual(list(self.uint_array("events", 16))[:2], [1, 4])

    def test_timer_pointer_uses_the_32_bit_firmware_message_abi(self) -> None:
        self.use_queue()
        self.submit(timer=0x12345678ABCDEF01)
        self.assertEqual(
            list(self.uint_array("message", 3)),
            [4, 0x3456789A, 0xABCDEF01],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "40b0215e7ae4fd177404e9162f9e7774c04732995601e2b68c28dc8d160bb25a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "36a088f14bf3bebd160ca3f453e91875a2b89f10dc143fc8406146eb62ff0cad",
        )


if __name__ == "__main__":
    unittest.main()
