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
SOURCE = COMPONENT_ROOT / "rtos_event_group_clear_from_isr.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_clear_from_isr_host.c"
)


class RtosEventGroupClearFromIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_clear_from_isr.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_clear_from_isr.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_clear_from_isr_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_result = (
            cls.loaded
            .open_cfw_test_rtos_event_group_clear_from_isr_set_result
        )
        cls.set_result.argtypes = [ctypes.c_int]
        cls.set_result.restype = None
        cls.clear_from_isr = (
            cls.loaded.open_cfw_rtos_event_group_clear_from_isr
        )
        cls.clear_from_isr.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.clear_from_isr.restype = ctypes.c_int
        cls.clear_callback = (
            cls.loaded.open_cfw_rtos_event_group_clear_callback
        )
        cls.clear_callback.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.clear_callback.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_clear_from_isr_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_clear_from_isr_{suffix}",
        )

    def test_forwards_exact_callback_group_bits_and_null_wake_pointer(
        self,
    ) -> None:
        self.set_result(1)
        self.assertEqual(self.clear_from_isr(0x12345678, 0x89ABCDEF), 1)
        self.assertEqual(self.uint("calls").value, 1)
        self.assertEqual(
            self.uintptr("callback").value,
            ctypes.cast(self.clear_callback, ctypes.c_void_p).value,
        )
        self.assertEqual(self.uintptr("group").value, 0x12345678)
        self.assertEqual(self.uint("bits").value, 0x89ABCDEF)
        self.assertEqual(self.uintptr("wake_pointer").value, 0)

    def test_returns_the_pended_submission_result_unchanged(self) -> None:
        for result in (-0x1234567, -1, 0, 1, 0x1234567):
            with self.subTest(result=result):
                self.reset_fixture()
                self.set_result(result)
                self.assertEqual(
                    self.clear_from_isr(0x20000000, 3),
                    result,
                )

    def test_wrapper_performs_no_group_or_mask_validation(self) -> None:
        for group, bits in (
            (0, 0),
            (0, 0xFFFFFFFF),
            (0x20001234, 0xFF000000),
        ):
            with self.subTest(group=group, bits=bits):
                self.reset_fixture()
                self.set_result(7)
                self.assertEqual(self.clear_from_isr(group, bits), 7)
                self.assertEqual(self.uint("calls").value, 1)
                self.assertEqual(self.uintptr("group").value, group)
                self.assertEqual(self.uint("bits").value, bits)
                self.assertEqual(self.uintptr("wake_pointer").value, 0)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "1e858111aff7b7bd87a8fa985c2c84d05963a861b0d271f5be5a9191aeb44787",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5b6300847f484a0ed5623d845ae318c12d858c24e02ce7ae0c44d3d30e95b0df",
        )


if __name__ == "__main__":
    unittest.main()
