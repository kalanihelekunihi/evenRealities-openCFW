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
SOURCE = COMPONENT_ROOT / "rtos_event_group_wait.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_wait_host.c"
)


class RtosEventGroupWaitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_wait.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_wait.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_wait_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_group_bits = (
            cls.loaded.open_cfw_test_rtos_event_group_wait_set_group_bits
        )
        cls.set_group_bits.argtypes = [ctypes.c_uint]
        cls.set_group_bits.restype = None
        cls.set_scheduler_state = (
            cls.loaded
            .open_cfw_test_rtos_event_group_wait_set_scheduler_state
        )
        cls.set_scheduler_state.argtypes = [ctypes.c_uint]
        cls.set_scheduler_state.restype = None
        cls.set_resume_result = (
            cls.loaded.open_cfw_test_rtos_event_group_wait_set_resume_result
        )
        cls.set_resume_result.argtypes = [ctypes.c_uint]
        cls.set_resume_result.restype = None
        cls.set_reset_value = (
            cls.loaded.open_cfw_test_rtos_event_group_wait_set_reset_value
        )
        cls.set_reset_value.argtypes = [ctypes.c_uint]
        cls.set_reset_value.restype = None
        cls.set_reset_new_bits = (
            cls.loaded.open_cfw_test_rtos_event_group_wait_set_reset_new_bits
        )
        cls.set_reset_new_bits.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_reset_new_bits.restype = None
        cls.wait = cls.loaded.open_cfw_rtos_event_group_wait
        cls.wait.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.wait.restype = ctypes.c_uint
        cls.group = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_wait_group",
        )
        cls.group_address = ctypes.addressof(cls.group)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_wait_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_wait_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_wait_{suffix}",
        )
        return list(values)

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        return cls.array("events", 64)[:count]

    def invoke(
        self,
        *,
        group: int | None = None,
        bits: int = 3,
        clear: int = 0,
        all_bits: int = 0,
        ticks: int = 0,
    ) -> int:
        group_pointer = self.group_address if group is None else group
        return self.wait(
            group_pointer,
            bits,
            clear,
            all_bits,
            ticks,
        )

    def test_immediate_any_bit_match_returns_complete_snapshot(
        self,
    ) -> None:
        self.set_group_bits(0xA)
        self.assertEqual(self.invoke(bits=3, ticks=9), 0xA)
        self.assertEqual(self.events(), [20, 30, 40, 70])
        self.assertEqual(self.uint("write_calls").value, 0)
        self.assertEqual(self.uint("place_calls").value, 0)
        self.assertEqual(self.uint("reset_calls").value, 0)

    def test_immediate_all_bit_match_clears_only_requested_bits(
        self,
    ) -> None:
        self.set_group_bits(0xF)
        self.assertEqual(
            self.invoke(bits=3, clear=1, all_bits=1, ticks=9),
            0xF,
        )
        self.assertEqual(self.events(), [20, 30, 40, 50, 70])
        self.assertEqual(self.group[0], 0xC)
        self.assertEqual(self.uint("last_write").value, 0xC)

    def test_zero_timeout_poll_returns_nonmatching_current_bits(
        self,
    ) -> None:
        self.set_group_bits(4)
        self.assertEqual(self.invoke(bits=3, ticks=0), 4)
        self.assertEqual(self.events(), [20, 30, 40, 70])
        self.assertEqual(self.uint("place_calls").value, 0)
        self.assertEqual(self.uint("reset_calls").value, 0)

    def test_blocking_wait_encodes_exact_control_bits_and_list_address(
        self,
    ) -> None:
        for clear, all_bits, expected_control in (
            (0, 0, 0x00000003),
            (1, 0, 0x01000003),
            (0, 1, 0x04000003),
            (1, 1, 0x05000003),
        ):
            with self.subTest(clear=clear, all_bits=all_bits):
                self.reset_fixture()
                self.set_reset_value(0x02000005)
                result = self.invoke(
                    bits=3,
                    clear=clear,
                    all_bits=all_bits,
                    ticks=0x12345678,
                )
                self.assertEqual(result, 5)
                self.assertEqual(self.events(), [20, 30, 40, 60, 70, 90])
                self.assertEqual(
                    self.uint("last_place_value").value,
                    expected_control,
                )
                self.assertEqual(
                    self.uint("last_place_ticks").value,
                    0x12345678,
                )
                self.assertEqual(
                    self.uintptr("last_place_list").value,
                    self.group_address + 4,
                )

    def test_resume_without_internal_yield_requests_explicit_yield(
        self,
    ) -> None:
        self.set_resume_result(0)
        self.set_reset_value(0x02000001)
        self.assertEqual(self.invoke(bits=1, ticks=7), 1)
        self.assertEqual(self.events(), [20, 30, 40, 60, 70, 80, 90])
        self.assertEqual(self.uint("yield_calls").value, 1)

    def test_timeout_rereads_and_clears_matching_bits_inside_critical(
        self,
    ) -> None:
        self.set_reset_value(0)
        self.set_reset_new_bits(1, 0xF)
        self.assertEqual(
            self.invoke(bits=3, clear=1, all_bits=1, ticks=7),
            0xF,
        )
        self.assertEqual(
            self.events(),
            [20, 30, 40, 60, 70, 90, 100, 40, 50, 110],
        )
        self.assertEqual(self.group[0], 0xC)
        self.assertEqual(
            self.array("event_depths", 64)[6:10],
            [1, 1, 1, 1],
        )
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_timeout_reread_returns_nonmatching_bits_without_clear(
        self,
    ) -> None:
        self.set_reset_new_bits(1, 4)
        self.assertEqual(
            self.invoke(bits=3, clear=1, all_bits=0, ticks=7),
            4,
        )
        self.assertEqual(
            self.events(),
            [20, 30, 40, 60, 70, 90, 100, 40, 110],
        )
        self.assertEqual(self.uint("write_calls").value, 0)

    def test_invalid_group_or_wait_mask_fail_stops_before_scheduler(
        self,
    ) -> None:
        invalid = (
            (0, 1),
            (self.group_address, 0),
            (self.group_address, 0x01000001),
            (self.group_address, 0xFF000000),
        )
        for group, bits in invalid:
            with self.subTest(group=group, bits=bits):
                self.reset_fixture()
                self.assertEqual(
                    self.invoke(group=group, bits=bits, ticks=0),
                    0,
                )
                self.assertEqual(self.events(), [10])
                self.assertEqual(self.uint("fail_stop_calls").value, 1)
                self.assertEqual(self.uint("scheduler_reads").value, 0)
                self.assertEqual(self.uint("suspend_calls").value, 0)

    def test_suspended_scheduler_rejects_only_nonzero_timeout(
        self,
    ) -> None:
        self.set_scheduler_state(0)
        self.assertEqual(self.invoke(bits=1, ticks=1), 0)
        self.assertEqual(self.events(), [20, 10])
        self.assertEqual(self.uint("suspend_calls").value, 0)

        self.reset_fixture()
        self.set_scheduler_state(0)
        self.assertEqual(self.invoke(bits=1, ticks=0), 0)
        self.assertEqual(self.events(), [20, 30, 40, 70])

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "fe9bef7f143774efc74e34d8d54102175f89d141631f2447aa32a4f715555ee4",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "8fc4f25f47175d5cfe2152bca41c35b493dbd45db4f314fead80a9b2e2a2fb97",
        )


if __name__ == "__main__":
    unittest.main()
