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
SOURCE = COMPONENT_ROOT / "rtos_timer_service_loop.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_service_loop_host.c"
)


class RtosTimerServiceLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_service_loop.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_service_loop.so"
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
            cls.loaded.open_cfw_test_rtos_timer_service_loop_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.service_loop = cls.loaded.open_cfw_rtos_timer_service_loop
        cls.service_loop.argtypes = [ctypes.c_void_p]
        cls.service_loop.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_service_loop_{suffix}",
        )

    @classmethod
    def array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_service_loop_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        return list(cls.array("events", 64))[:count]

    def configure(
        self,
        *,
        expiries: tuple[int, ...],
        empty_values: tuple[int, ...],
    ) -> None:
        self.assertEqual(len(expiries), len(empty_values))
        self.uint("iteration_limit").value = len(expiries)
        expiry_array = self.array("expiries", 16)
        empty_array = self.array("empty_values", 16)
        for index, (expiry, empty) in enumerate(
            zip(expiries, empty_values)
        ):
            expiry_array[index] = expiry
            empty_array[index] = empty

    def run_loop(self, argument: int = 0x12345678) -> None:
        self.service_loop(argument)

    def test_one_iteration_preserves_exact_operation_order(self) -> None:
        self.configure(expiries=(123,), empty_values=(1,))
        self.run_loop()
        self.assertEqual(self.events(), [10, 20, 30, 40])
        self.assertEqual(self.uint("query_calls").value, 1)
        self.assertEqual(self.uint("wait_calls").value, 1)
        self.assertEqual(self.uint("command_calls").value, 1)
        self.assertEqual(self.uint("continue_calls").value, 1)
        self.assertEqual(self.array("wait_expiries", 16)[0], 123)
        self.assertEqual(self.array("wait_empty_values", 16)[0], 1)

    def test_every_iteration_queries_fresh_values(self) -> None:
        self.configure(
            expiries=(7, 11, 19),
            empty_values=(0, 1, 0),
        )
        self.run_loop()
        self.assertEqual(
            self.events(),
            [10, 20, 30, 40] * 3,
        )
        self.assertEqual(
            list(self.array("wait_expiries", 16))[:3],
            [7, 11, 19],
        )
        self.assertEqual(
            list(self.array("wait_empty_values", 16))[:3],
            [0, 1, 0],
        )

    def test_full_width_query_results_are_forwarded(self) -> None:
        self.configure(
            expiries=(0, 0xFFFFFFFF),
            empty_values=(0xFFFFFFFF, 0x80000000),
        )
        self.run_loop()
        self.assertEqual(
            list(self.array("wait_expiries", 16))[:2],
            [0, 0xFFFFFFFF],
        )
        self.assertEqual(
            list(self.array("wait_empty_values", 16))[:2],
            [0xFFFFFFFF, 0x80000000],
        )

    def test_command_drain_runs_once_after_each_wait(self) -> None:
        self.configure(
            expiries=(1, 2, 3, 4),
            empty_values=(0, 0, 0, 0),
        )
        self.run_loop()
        self.assertEqual(self.uint("wait_calls").value, 4)
        self.assertEqual(self.uint("command_calls").value, 4)
        self.assertEqual(self.uint("continue_calls").value, 4)

    def test_thread_argument_is_ignored(self) -> None:
        self.configure(expiries=(5,), empty_values=(0,))
        for argument in (0, 1, 0xFFFFFFFF, 0x123456789ABCDEF0):
            with self.subTest(argument=argument):
                self.reset_fixture()
                self.configure(expiries=(5,), empty_values=(0,))
                self.run_loop(argument)
                self.assertEqual(self.array("wait_expiries", 16)[0], 5)
                self.assertEqual(self.events(), [10, 20, 30, 40])

    def test_empty_and_nonempty_list_flags_do_not_change_loop_order(
        self,
    ) -> None:
        self.configure(
            expiries=(0, 99),
            empty_values=(1, 0),
        )
        self.run_loop()
        self.assertEqual(
            self.events(),
            [10, 20, 30, 40, 10, 20, 30, 40],
        )

    def test_fixture_stops_only_after_a_complete_iteration(self) -> None:
        self.configure(expiries=(42,), empty_values=(0,))
        self.run_loop()
        self.assertEqual(self.events()[-2:], [30, 40])
        self.assertEqual(self.uint("command_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "940811c19d3b1d85f9bfddf0b78b5c087425179ebb9b30430d8569f675d77ad9",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "cc4978477539c8c4d51cbfbd3078136a86562d672ededc7ac96bdb93ad872843",
        )


if __name__ == "__main__":
    unittest.main()
