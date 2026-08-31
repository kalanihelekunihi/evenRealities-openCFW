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
SOURCE = COMPONENT_ROOT / "rtos_event_group_set_from_isr.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_set_from_isr_host.c"
)


class RtosEventGroupSetFromIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_set_from_isr.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_set_from_isr.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_set_from_isr_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_result = (
            cls.loaded.open_cfw_test_rtos_event_group_set_from_isr_set_result
        )
        cls.set_result.argtypes = [ctypes.c_int]
        cls.set_result.restype = None
        cls.set_from_isr = (
            cls.loaded.open_cfw_rtos_event_group_set_from_isr
        )
        cls.set_from_isr.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_int),
        ]
        cls.set_from_isr.restype = ctypes.c_int
        cls.set_callback = (
            cls.loaded.open_cfw_rtos_event_group_set_callback
        )
        cls.set_callback.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_callback.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_set_from_isr_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_set_from_isr_{suffix}",
        )

    def test_forwards_exact_callback_group_bits_and_wake_pointer(
        self,
    ) -> None:
        wake = ctypes.c_int(0)
        self.set_result(1)
        self.assertEqual(
            self.set_from_isr(0x12345678, 0x89ABCDEF, wake),
            1,
        )
        self.assertEqual(self.uint("calls").value, 1)
        self.assertEqual(
            self.uintptr("callback").value,
            ctypes.cast(self.set_callback, ctypes.c_void_p).value,
        )
        self.assertEqual(self.uintptr("group").value, 0x12345678)
        self.assertEqual(self.uint("bits").value, 0x89ABCDEF)
        self.assertEqual(
            self.uintptr("wake_pointer").value,
            ctypes.addressof(wake),
        )

    def test_returns_the_pended_submission_result_unchanged(self) -> None:
        wake = ctypes.c_int(0)
        for result in (-0x1234567, -1, 0, 1, 0x1234567):
            with self.subTest(result=result):
                self.reset_fixture()
                self.set_result(result)
                self.assertEqual(
                    self.set_from_isr(0x20000000, 3, wake),
                    result,
                )

    def test_wrapper_performs_no_argument_validation(self) -> None:
        for group, bits, wake_pointer in (
            (0, 0, None),
            (0, 0xFFFFFFFF, None),
            (0x20001234, 0xFF000000, ctypes.pointer(ctypes.c_int())),
        ):
            with self.subTest(group=group, bits=bits):
                self.reset_fixture()
                self.set_result(7)
                self.assertEqual(
                    self.set_from_isr(group, bits, wake_pointer),
                    7,
                )
                self.assertEqual(self.uint("calls").value, 1)
                self.assertEqual(self.uintptr("group").value, group)
                self.assertEqual(self.uint("bits").value, bits)
                self.assertEqual(
                    self.uintptr("wake_pointer").value,
                    (
                        0
                        if wake_pointer is None
                        else ctypes.addressof(wake_pointer.contents)
                    ),
                )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "5853bf0f096d94459ea95573e7420b2ba30f0e58bf37dfc4809880edebeba59b",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "8ac78b2729f95f99c3200563fa7479767fa209a22d50680da459e0690b058043",
        )


if __name__ == "__main__":
    unittest.main()
