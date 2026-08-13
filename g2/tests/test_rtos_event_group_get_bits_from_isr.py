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
SOURCE = COMPONENT_ROOT / "rtos_event_group_get_bits_from_isr.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_get_bits_from_isr_host.c"
)


class RtosEventGroupGetBitsFromIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_get_bits_from_isr.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_get_bits_from_isr.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_get_bits_from_isr_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_values = (
            cls.loaded
            .open_cfw_test_rtos_event_group_get_bits_from_isr_set_values
        )
        cls.set_values.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.set_values.restype = None
        cls.get_bits = (
            cls.loaded.open_cfw_rtos_event_group_get_bits_from_isr
        )
        cls.get_bits.argtypes = [ctypes.c_void_p]
        cls.get_bits.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_get_bits_from_isr_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_get_bits_from_isr_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        values = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_get_bits_from_isr_events",
        )
        return list(values)[:cls.uint("event_count").value]

    def test_reads_once_between_mask_save_and_restore(self) -> None:
        self.set_values(0x12345678, 0x89ABCDEF)
        self.assertEqual(self.get_bits(0x20001234), 0x89ABCDEF)
        self.assertEqual(self.events(), [10, 20, 30])
        self.assertEqual(self.uint("set_calls").value, 1)
        self.assertEqual(self.uint("read_calls").value, 1)
        self.assertEqual(self.uint("restore_calls").value, 1)
        self.assertEqual(self.uint("restored_mask").value, 0x12345678)
        self.assertEqual(self.uintptr("group").value, 0x20001234)

    def test_all_bit_patterns_are_returned_unchanged(self) -> None:
        for bits in (0, 1, 0x00FFFFFF, 0x80000000, 0xFFFFFFFF):
            with self.subTest(bits=bits):
                self.reset_fixture()
                self.set_values(0x30, bits)
                self.assertEqual(self.get_bits(0x20000000), bits)

    def test_full_saved_mask_is_forwarded_to_restore(self) -> None:
        for mask in (0, 0x30, 0x80000000, 0xFFFFFFFF):
            with self.subTest(mask=mask):
                self.reset_fixture()
                self.set_values(mask, 7)
                self.assertEqual(self.get_bits(0x20000000), 7)
                self.assertEqual(self.uint("restored_mask").value, mask)

    def test_null_group_is_not_validated_by_the_wrapper(self) -> None:
        self.set_values(0x30, 0x55AA55AA)
        self.assertEqual(self.get_bits(0), 0x55AA55AA)
        self.assertEqual(self.events(), [10, 20, 30])
        self.assertEqual(self.uintptr("group").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "6afc615fe8e6f10766a1f9b09e01d555ad8516952d35c73a511efc44866500e1",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9b84d0f91211a18f90d855b36f45e58083ecbaa8a24ef3cb1a46837668a93e00",
        )


if __name__ == "__main__":
    unittest.main()
