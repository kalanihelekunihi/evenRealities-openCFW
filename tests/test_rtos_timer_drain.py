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
SOURCE = COMPONENT_ROOT / "rtos_timer_drain.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "rtos_timer_drain_host.c"


class RtosTimerDrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_drain.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_drain.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_drain_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.drain = cls.loaded.open_cfw_test_rtos_timer_drain_run
        cls.drain.argtypes = []
        cls.drain.restype = None
        for suffix in (
            "message_size",
            "timer_offset",
            "parameter_two_offset",
        ):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_rtos_timer_drain_{suffix}",
            )
            function.argtypes = []
            function.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_drain_{suffix}",
        )

    @classmethod
    def uint_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_drain_{suffix}",
        )

    @classmethod
    def pointer_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_void_p]:
        return (ctypes.c_void_p * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_drain_{suffix}",
        )

    @classmethod
    def timer(cls) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * 11).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_timer_drain_timer",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        return list(cls.uint_array("events", 256))[:count]

    def configure_messages(
        self,
        messages: tuple[tuple[int, int, int, int], ...],
        receive_results: tuple[int, ...] | None = None,
    ) -> None:
        words = self.uint_array("messages", 64)
        results = self.uint_array("receive_results", 17)
        self.uint("message_count").value = len(messages)
        for index, message in enumerate(messages):
            for word_index, value in enumerate(message):
                words[index * 4 + word_index] = value & 0xFFFFFFFF
            results[index] = (
                receive_results[index]
                if receive_results is not None
                else 1
            )
        results[len(messages)] = 0

    def run_one(
        self,
        command: int,
        value: int = 0,
        timer_token: int = 0x12345678,
    ) -> None:
        self.configure_messages(((command, value, timer_token, 0),))
        self.drain()

    def test_message_abi_and_empty_queue_are_exact(self) -> None:
        self.assertEqual(
            self.loaded.open_cfw_test_rtos_timer_drain_message_size(),
            16,
        )
        self.assertEqual(
            self.loaded.open_cfw_test_rtos_timer_drain_timer_offset(),
            8,
        )
        self.assertEqual(
            self.loaded.open_cfw_test_rtos_timer_drain_parameter_two_offset(),
            12,
        )
        self.configure_messages(())
        self.drain()
        self.assertEqual(self.events(), [10, 20])
        self.assertEqual(self.uint("queue_reads").value, 1)
        self.assertEqual(self.uint("receive_calls").value, 1)
        self.assertEqual(self.uint_array("receive_ticks", 17)[0], 0)

    def test_every_negative_id_executes_the_exact_pended_callback(self) -> None:
        messages = (
            (-1, 0x11111111, 0x22222222, 0x33333333),
            (-2, 0x44444444, 0x55555555, 0x66666666),
            (-0x80000000, 0x77777777, 0x88888888, 0x99999999),
        )
        self.configure_messages(
            messages,
            receive_results=(1, 2, 0xFFFFFFFF),
        )
        queues = self.pointer_array("queue_values", 17)
        for index, value in enumerate((0x1000, 0x2000, 0x3000, 0x4000)):
            queues[index] = value
        self.drain()
        self.assertEqual(
            self.events(),
            [10, 20, 30, 10, 20, 30, 10, 20, 30, 10, 20],
        )
        self.assertEqual(self.uint("pended_calls").value, 3)
        self.assertEqual(
            list(self.uint_array("pended_functions", 17))[:3],
            [0x11111111, 0x44444444, 0x77777777],
        )
        self.assertEqual(
            list(self.uint_array("pended_parameter_one", 17))[:3],
            [0x22222222, 0x55555555, 0x88888888],
        )
        self.assertEqual(
            list(self.uint_array("pended_parameter_two", 17))[:3],
            [0x33333333, 0x66666666, 0x99999999],
        )
        self.assertEqual(self.uint("timer_maps").value, 0)
        self.assertEqual(self.uint("sample_calls").value, 0)
        self.assertEqual(
            list(self.pointer_array("received_queues", 17))[:4],
            [0x1000, 0x2000, 0x3000, 0x4000],
        )

    def test_nonnegative_commands_remove_before_sample_even_if_unknown(
        self,
    ) -> None:
        timer = self.timer()
        timer[5] = 0xABCDEF01
        self.configure_messages(
            (
                (0, 1, 0xAAAA0001, 0),
                (10, 2, 0xAAAA0002, 0),
            )
        )
        samples = self.uint_array("sample_values", 17)
        samples[0] = 7
        samples[1] = 8
        self.drain()
        timer_address = ctypes.addressof(timer)
        self.assertEqual(self.uint("container_reads").value, 2)
        self.assertEqual(self.uint("remove_calls").value, 2)
        self.assertEqual(
            list(self.pointer_array("removed_items", 17))[:2],
            [timer_address + 4, timer_address + 4],
        )
        self.assertEqual(self.uint("sample_calls").value, 2)
        self.assertEqual(self.uint("status_reads").value, 0)
        self.assertEqual(self.uint("insert_calls").value, 0)
        self.assertEqual(
            self.events()[:10],
            [10, 20, 40, 50, 60, 10, 20, 40, 50, 60],
        )

    def test_start_and_reset_commands_share_the_stock_insert_path(
        self,
    ) -> None:
        for command in (1, 2, 6, 7):
            with self.subTest(command=command):
                self.reset_fixture()
                timer = self.timer()
                timer[6] = 7
                timer[10] = 0xA0
                self.uint_array("sample_values", 17)[0] = 42
                self.run_one(command, value=100)
                self.assertEqual(timer[10] & 0xFF, 0xA1)
                self.assertEqual(self.uint("insert_calls").value, 1)
                self.assertEqual(
                    self.uint_array("insert_next_expiry", 17)[0],
                    107,
                )
                self.assertEqual(
                    self.uint_array("insert_time_now", 17)[0],
                    42,
                )
                self.assertEqual(
                    self.uint_array("insert_command_time", 17)[0],
                    100,
                )
                self.assertEqual(self.uint("callback_calls").value, 0)
                self.assertEqual(self.uint("reload_calls").value, 0)

    def test_expired_one_shot_uses_fresh_status_then_calls_back(self) -> None:
        timer = self.timer()
        timer[6] = 5
        timer[10] = 0x80
        self.uint_array("sample_values", 17)[0] = 200
        self.uint_array("insert_results", 17)[0] = 1
        self.uint("insert_mutate_status_call").value = 0
        self.uint("insert_status_value").value = 0xA3
        self.run_one(1, value=100)
        self.assertEqual(timer[10] & 0xFF, 0xA2)
        self.assertEqual(
            list(self.uint_array("status_read_values", 32))[:3],
            [0x80, 0xA3, 0xA3],
        )
        self.assertEqual(
            list(self.uint_array("status_write_values", 32))[:2],
            [0x81, 0xA2],
        )
        self.assertEqual(self.uint("reload_calls").value, 0)
        self.assertEqual(self.uint("callback_calls").value, 1)
        self.assertLess(
            self.events().index(110),
            self.events().index(130),
        )

    def test_expired_autoreload_rereads_period_before_reload(self) -> None:
        timer = self.timer()
        timer[6] = 5
        self.uint_array("sample_values", 17)[0] = 200
        self.uint_array("insert_results", 17)[0] = 1
        self.uint("insert_mutate_status_call").value = 0
        self.uint("insert_status_value").value = 0xE5
        self.uint("insert_mutate_period_call").value = 0
        self.uint("insert_period_value").value = 9
        self.run_one(2, value=100)
        self.assertEqual(
            list(self.uint_array("period_read_values", 32))[:2],
            [5, 9],
        )
        self.assertEqual(self.uint("reload_calls").value, 1)
        self.assertEqual(
            self.uint_array("reload_next_expiry", 17)[0],
            109,
        )
        self.assertEqual(
            self.uint_array("reload_time_now", 17)[0],
            200,
        )
        self.assertEqual(self.uint("callback_calls").value, 1)
        self.assertEqual(timer[10] & 0xFF, 0xE5)
        self.assertLess(
            self.events().index(120),
            self.events().index(130),
        )

    def test_stop_commands_clear_only_the_active_bit(self) -> None:
        for command in (3, 8):
            with self.subTest(command=command):
                self.reset_fixture()
                timer = self.timer()
                timer[10] = 0xFF
                self.run_one(command)
                self.assertEqual(timer[10] & 0xFF, 0xFE)
                self.assertEqual(self.uint("insert_calls").value, 0)
                self.assertEqual(self.uint("callback_calls").value, 0)

    def test_change_period_commands_use_current_time_as_reference(self) -> None:
        for command in (4, 9):
            with self.subTest(command=command):
                self.reset_fixture()
                timer = self.timer()
                timer[10] = 0xA0
                self.uint_array("sample_values", 17)[0] = 0xFFFFFFFE
                self.uint_array("insert_results", 17)[0] = 0xFFFFFFFF
                self.run_one(command, value=5)
                self.assertEqual(timer[6], 5)
                self.assertEqual(timer[10] & 0xFF, 0xA1)
                self.assertEqual(
                    list(self.uint_array("period_read_values", 32))[:2],
                    [5, 5],
                )
                self.assertEqual(
                    self.uint_array("insert_next_expiry", 17)[0],
                    3,
                )
                self.assertEqual(
                    self.uint_array("insert_time_now", 17)[0],
                    0xFFFFFFFE,
                )
                self.assertEqual(
                    self.uint_array("insert_command_time", 17)[0],
                    0xFFFFFFFE,
                )
                self.assertEqual(self.uint("callback_calls").value, 0)

    def test_zero_change_period_takes_the_fail_stop_path(self) -> None:
        self.uint_array("sample_values", 17)[0] = 123
        self.run_one(4, value=0)
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("insert_calls").value, 0)
        self.assertEqual(self.events()[-1], 150)

    def test_delete_frees_dynamic_or_deactivates_static_timer(self) -> None:
        timer = self.timer()
        timer[10] = 0xA1
        self.run_one(5)
        self.assertEqual(self.uint("free_calls").value, 1)
        self.assertEqual(timer[10] & 0xFF, 0xA1)

        self.reset_fixture()
        timer = self.timer()
        timer[10] = 0xA3
        self.run_one(5)
        self.assertEqual(self.uint("free_calls").value, 0)
        self.assertEqual(timer[10] & 0xFF, 0xA2)
        self.assertEqual(
            list(self.uint_array("status_read_values", 32))[:2],
            [0xA3, 0xA3],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "bb8582927cf796d6e88805e2385cd81412c43c4dfb36959bc6f18c761bebd3f0",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ba99b9951c8cb8618f0b46603804b2528448ed02ca5890cba890175388eb12a3",
        )


if __name__ == "__main__":
    unittest.main()
