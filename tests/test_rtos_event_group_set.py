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
SOURCE = COMPONENT_ROOT / "rtos_event_group_set.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_set_host.c"
)


class RtosEventGroupSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_set.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_set.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_set_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_bits = (
            cls.loaded.open_cfw_test_rtos_event_group_set_set_bits
        )
        cls.set_bits.argtypes = [ctypes.c_uint]
        cls.set_bits.restype = None
        cls.set_head = (
            cls.loaded.open_cfw_test_rtos_event_group_set_set_head
        )
        cls.set_head.argtypes = [ctypes.c_uint]
        cls.set_head.restype = None
        cls.set_item = (
            cls.loaded.open_cfw_test_rtos_event_group_set_set_item
        )
        cls.set_item.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.set_item.restype = None
        cls.set_remove_mutation = (
            cls.loaded
            .open_cfw_test_rtos_event_group_set_set_remove_mutation
        )
        cls.set_remove_mutation.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.set_remove_mutation.restype = None
        cls.set_resume_mutation = (
            cls.loaded
            .open_cfw_test_rtos_event_group_set_set_resume_mutation
        )
        cls.set_resume_mutation.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.set_resume_mutation.restype = None
        cls.set_group_bits = (
            cls.loaded.open_cfw_rtos_event_group_set
        )
        cls.set_group_bits.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_group_bits.restype = ctypes.c_uint
        cls.group = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_set_bits",
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
            f"open_cfw_test_rtos_event_group_set_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_set_{suffix}",
        )
        return list(values)

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        return cls.array("events", 128)[:count]

    def invoke(
        self,
        bits: int,
        group: int | None = None,
    ) -> int:
        group_pointer = self.group_address if group is None else group
        return self.set_group_bits(group_pointer, bits)

    def configure_chain(
        self,
        values: list[int],
    ) -> None:
        self.set_head(0 if values else 7)
        for index, value in enumerate(values):
            next_index = index + 1 if index + 1 < len(values) else 7
            self.set_item(index, value, next_index)

    def test_empty_wait_list_sets_bits_and_returns_post_resume_value(
        self,
    ) -> None:
        self.set_bits(0xA0)
        self.assertEqual(self.invoke(0x05), 0xA5)
        self.assertEqual(
            self.events(),
            [20, 30, 40, 50, 30, 40, 90, 30],
        )
        self.assertEqual(self.uint("suspend_calls").value, 1)
        self.assertEqual(self.uint("resume_calls").value, 1)
        self.assertEqual(self.uint("last_write").value, 0xA5)
        self.assertEqual(self.uint("remove_calls").value, 0)

    def test_any_and_all_waiters_are_matched_independently(self) -> None:
        self.set_bits(0x08)
        self.configure_chain([
            0x00000002,
            0x04000003,
            0x04000007,
            0x00000040,
        ])
        self.assertEqual(self.invoke(0x03), 0x0B)
        self.assertEqual(self.uint("next_calls").value, 4)
        self.assertEqual(self.uint("value_calls").value, 4)
        self.assertEqual(self.uint("remove_calls").value, 2)
        self.assertEqual(
            self.array("removed_indices", 8)[:2],
            [0, 1],
        )
        self.assertEqual(
            self.array("removed_values", 8)[:2],
            [0x0200000B, 0x0200000B],
        )

    def test_clear_on_exit_accumulates_all_matched_wait_masks(
        self,
    ) -> None:
        self.set_bits(0x08)
        self.configure_chain([
            0x01000001,
            0x05000003,
            0x00000008,
        ])
        self.assertEqual(self.invoke(0x03), 0x08)
        self.assertEqual(self.uint("remove_calls").value, 3)
        self.assertEqual(
            self.array("removed_values", 8)[:3],
            [0x0200000B, 0x0200000B, 0x0200000B],
        )
        self.assertEqual(self.uint("last_write").value, 0x08)

    def test_next_item_is_cached_before_a_matching_item_is_removed(
        self,
    ) -> None:
        self.configure_chain([1, 1])
        self.assertEqual(self.invoke(1), 1)
        self.assertEqual(
            self.array("removed_indices", 8)[:2],
            [0, 1],
        )
        self.assertEqual(self.uint("next_calls").value, 2)

    def test_each_waiter_observes_fresh_bits_after_prior_removal(
        self,
    ) -> None:
        self.configure_chain([
            0x00000001,
            0x05000004,
        ])
        self.set_remove_mutation(1, 0x05)
        self.assertEqual(self.invoke(1), 1)
        self.assertEqual(
            self.array("removed_values", 8)[:2],
            [0x02000001, 0x02000005],
        )
        self.assertEqual(self.uint("last_write").value, 1)

    def test_zero_set_mask_is_valid_and_can_unblock_existing_bits(
        self,
    ) -> None:
        self.set_bits(4)
        self.configure_chain([4])
        self.assertEqual(self.invoke(0), 4)
        self.assertEqual(self.uint("remove_calls").value, 1)
        self.assertEqual(
            self.array("removed_values", 8)[0],
            0x02000004,
        )

    def test_return_value_is_read_after_scheduler_resume(self) -> None:
        self.set_bits(1)
        self.set_resume_mutation(1, 0xA5A55A5A)
        self.assertEqual(self.invoke(2), 0xA5A55A5A)
        self.assertEqual(self.uint("last_write").value, 3)
        self.assertEqual(self.events()[-2:], [90, 30])

    def test_invalid_group_or_control_mask_fail_stops_before_suspend(
        self,
    ) -> None:
        for group, bits in (
            (0, 1),
            (self.group_address, 0x01000000),
            (self.group_address, 0xFF000001),
        ):
            with self.subTest(group=group, bits=bits):
                self.reset_fixture()
                self.assertEqual(self.invoke(bits, group), 0)
                self.assertEqual(self.events(), [10])
                self.assertEqual(self.uint("fail_stop_calls").value, 1)
                self.assertEqual(self.uint("suspend_calls").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c5c8c4dc1e8e28df48361d10de0a5560febd0e8c56586b5c4cd06bac8fa9639e",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1d3a54589376481cd8260b0b5e41f9e42b7153cb503c09889b7937d5c0be0864",
        )


if __name__ == "__main__":
    unittest.main()
