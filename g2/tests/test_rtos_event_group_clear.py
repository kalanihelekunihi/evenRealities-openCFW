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
SOURCE = COMPONENT_ROOT / "rtos_event_group_clear.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_clear_host.c"
)


class RtosEventGroupClearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_clear.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_clear.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_clear_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_group_bits = (
            cls.loaded.open_cfw_test_rtos_event_group_clear_set_group_bits
        )
        cls.set_group_bits.argtypes = [ctypes.c_uint]
        cls.set_group_bits.restype = None
        cls.set_mutated_bits = (
            cls.loaded.open_cfw_test_rtos_event_group_clear_set_mutated_bits
        )
        cls.set_mutated_bits.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_mutated_bits.restype = None
        cls.clear = cls.loaded.open_cfw_rtos_event_group_clear
        cls.clear.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.clear.restype = ctypes.c_uint
        cls.group = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_clear_group",
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
            f"open_cfw_test_rtos_event_group_clear_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_clear_{suffix}",
        )

    @classmethod
    def array(cls, suffix: str, length: int) -> list[int]:
        values = (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_clear_{suffix}",
        )
        return list(values)

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        return cls.array("events", 16)[:count]

    def invoke(self, bits: int, group: int | None = None) -> int:
        group_pointer = self.group_address if group is None else group
        return self.clear(group_pointer, bits)

    def test_clear_returns_preclear_snapshot_and_updates_group(self) -> None:
        self.set_group_bits(0xAF)
        self.assertEqual(self.invoke(0x0F), 0xAF)
        self.assertEqual(self.group[0], 0xA0)
        self.assertEqual(self.events(), [20, 30, 30, 40, 50])
        self.assertEqual(self.uint("last_write").value, 0xA0)
        self.assertEqual(self.uintptr("last_read_group").value, self.group_address)
        self.assertEqual(
            self.uintptr("last_write_group").value,
            self.group_address,
        )
        self.assertEqual(self.array("event_depths", 16)[:5], [1] * 5)
        self.assertEqual(self.uint("critical_depth").value, 0)

    def test_clear_uses_second_read_but_returns_first_snapshot(self) -> None:
        self.set_group_bits(0x0F)
        self.set_mutated_bits(1, 0xAA)
        self.assertEqual(self.invoke(0x03), 0x0F)
        self.assertEqual(self.group[0], 0xA8)
        self.assertEqual(self.uint("last_write").value, 0xA8)
        self.assertEqual(self.uint("read_calls").value, 2)

    def test_zero_mask_still_executes_the_atomic_read_write(self) -> None:
        self.set_group_bits(0x123456)
        self.assertEqual(self.invoke(0), 0x123456)
        self.assertEqual(self.group[0], 0x123456)
        self.assertEqual(self.events(), [20, 30, 30, 40, 50])
        self.assertEqual(self.uint("write_calls").value, 1)

    def test_all_low_24_bits_are_valid(self) -> None:
        self.set_group_bits(0xFFFFFFFF)
        self.assertEqual(self.invoke(0x00FFFFFF), 0xFFFFFFFF)
        self.assertEqual(self.group[0], 0xFF000000)
        self.assertEqual(self.uint("fail_stop_calls").value, 0)

    def test_invalid_group_or_control_bits_fail_before_critical(self) -> None:
        invalid = (
            (0, 1),
            (self.group_address, 0x01000000),
            (self.group_address, 0x80000001),
            (self.group_address, 0xFF000000),
        )
        for group, bits in invalid:
            with self.subTest(group=group, bits=bits):
                self.reset_fixture()
                self.assertEqual(self.invoke(bits, group), 0)
                self.assertEqual(self.events(), [10])
                self.assertEqual(self.uint("fail_stop_calls").value, 1)
                self.assertEqual(self.uint("enter_calls").value, 0)
                self.assertEqual(self.uint("read_calls").value, 0)
                self.assertEqual(self.uint("write_calls").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "a1da8c7fa16322e4bea2c1afdf0f77af962ee1117538e76a620adc31e99b47ad",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9afdef2109765c5b8aba1b88ae190705320d8ad22aee06684ae938517bb5c839",
        )


if __name__ == "__main__":
    unittest.main()
