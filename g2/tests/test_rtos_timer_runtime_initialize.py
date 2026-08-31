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
SOURCE = COMPONENT_ROOT / "rtos_timer_runtime_initialize.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_runtime_initialize_host.c"
)


class RtosTimerRuntimeInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_runtime_initialize.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_runtime_initialize.so"
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
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_queue = (
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_set_queue
        )
        cls.set_queue.argtypes = [ctypes.c_uint]
        cls.set_queue.restype = None
        cls.set_result = (
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_set_result
        )
        cls.set_result.argtypes = [ctypes.c_uint]
        cls.set_result.restype = None
        cls.queue_value = (
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_queue_value
        )
        cls.queue_value.argtypes = []
        cls.queue_value.restype = ctypes.c_uint
        cls.current_identity = (
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_current_identity
        )
        cls.current_identity.argtypes = []
        cls.current_identity.restype = ctypes.c_uint
        cls.overflow_identity = (
            cls.loaded.open_cfw_test_rtos_timer_runtime_init_overflow_identity
        )
        cls.overflow_identity.argtypes = []
        cls.overflow_identity.restype = ctypes.c_uint
        cls.storage_valid = (
            cls.loaded
            .open_cfw_test_rtos_timer_runtime_init_create_storage_valid
        )
        cls.storage_valid.argtypes = []
        cls.storage_valid.restype = ctypes.c_uint
        cls.control_valid = (
            cls.loaded
            .open_cfw_test_rtos_timer_runtime_init_create_control_valid
        )
        cls.control_valid.argtypes = []
        cls.control_valid.restype = ctypes.c_uint
        cls.list_identity = (
            cls.loaded
            .open_cfw_test_rtos_timer_runtime_init_list_argument_identity
        )
        cls.list_identity.argtypes = [ctypes.c_uint]
        cls.list_identity.restype = ctypes.c_uint
        cls.initialize = cls.loaded.open_cfw_rtos_timer_runtime_initialize
        cls.initialize.argtypes = []
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_runtime_init_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_runtime_init_{suffix}",
        )
        return list(values)

    def events(self) -> list[int]:
        return self.array("events", 32)[:self.uint("event_count").value]

    def test_existing_queue_only_enters_reads_and_exits(self) -> None:
        self.set_queue(0xA5A5A5A5)
        self.initialize()
        self.assertEqual(self.events(), [1, 2, 40])
        self.assertEqual(self.queue_value(), 0xA5A5A5A5)
        self.assertEqual(self.uint("list_calls").value, 0)
        self.assertEqual(self.uint("create_calls").value, 0)
        self.assertEqual(self.uint("queue_writes").value, 0)

    def test_null_queue_initializes_lists_and_static_queue_exactly(self) -> None:
        self.initialize()
        self.assertEqual(
            self.events(),
            [1, 2, 10, 11, 20, 21, 30, 31, 40],
        )
        self.assertEqual(self.list_identity(0), 1)
        self.assertEqual(self.list_identity(1), 2)
        self.assertEqual(self.current_identity(), 1)
        self.assertEqual(self.overflow_identity(), 2)
        self.assertEqual(self.uint("queue_length").value, 0x32)
        self.assertEqual(self.uint("item_size").value, 0x10)
        self.assertEqual(self.uint("queue_type").value, 0)
        self.assertEqual(self.storage_valid(), 1)
        self.assertEqual(self.control_valid(), 1)
        self.assertEqual(self.queue_value(), 0x12345678)

    def test_all_initialization_side_effects_stay_in_critical_section(
        self,
    ) -> None:
        self.initialize()
        self.assertEqual(
            self.array("event_depths", 32)[:9],
            [1] * 9,
        )
        self.assertEqual(self.uint("enter_calls").value, 1)
        self.assertEqual(self.uint("exit_calls").value, 1)
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_null_create_result_is_published_before_critical_exit(self) -> None:
        self.set_result(0)
        self.initialize()
        self.assertEqual(self.queue_value(), 0)
        self.assertEqual(self.uint("queue_writes").value, 1)
        self.assertEqual(self.events()[-2:], [31, 40])
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_successful_first_call_makes_later_calls_idempotent(self) -> None:
        self.initialize()
        self.initialize()
        self.assertEqual(
            self.events(),
            [1, 2, 10, 11, 20, 21, 30, 31, 40, 1, 2, 40],
        )
        self.assertEqual(self.uint("list_calls").value, 2)
        self.assertEqual(self.uint("create_calls").value, 1)
        self.assertEqual(self.uint("queue_reads").value, 2)
        self.assertEqual(self.uint("enter_calls").value, 2)
        self.assertEqual(self.uint("exit_calls").value, 2)

    def test_failed_create_is_retried_on_the_next_call(self) -> None:
        self.set_result(0)
        self.initialize()
        self.set_result(0xFFFFFFFF)
        self.initialize()
        self.assertEqual(self.uint("list_calls").value, 4)
        self.assertEqual(self.uint("create_calls").value, 2)
        self.assertEqual(self.uint("queue_writes").value, 2)
        self.assertEqual(self.queue_value(), 0xFFFFFFFF)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "8ef66a97e8390be6397ab443301f853244ebf919787bbdb7449c64202ba2065e",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "b4b741fbdc50f87a179ca1df46288a9fccc053e02f02ae70bb0fa9e9c74c7adf",
        )


if __name__ == "__main__":
    unittest.main()
