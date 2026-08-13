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
SOURCE = COMPONENT_ROOT / "rtos_event_group_set_callback.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_set_callback_host.c"
)


class RtosEventGroupSetCallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_set_callback.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_set_callback.so"
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
            cls.loaded.open_cfw_test_rtos_event_group_set_callback_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_result = (
            cls.loaded
            .open_cfw_test_rtos_event_group_set_callback_set_result
        )
        cls.set_result.argtypes = [ctypes.c_uint]
        cls.set_result.restype = None
        cls.callback = (
            cls.loaded.open_cfw_rtos_event_group_set_callback
        )
        cls.callback.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.callback.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_set_callback_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_set_callback_{suffix}",
        )

    def test_forwards_group_and_full_bit_mask_once(self) -> None:
        self.callback(0x20001234, 0x89ABCDEF)
        self.assertEqual(self.uint("calls").value, 1)
        self.assertEqual(self.uintptr("group").value, 0x20001234)
        self.assertEqual(self.uint("bits").value, 0x89ABCDEF)

    def test_null_group_and_zero_mask_are_not_prevalidated(self) -> None:
        self.callback(0, 0)
        self.assertEqual(self.uint("calls").value, 1)
        self.assertEqual(self.uintptr("group").value, 0)
        self.assertEqual(self.uint("bits").value, 0)

    def test_set_result_is_deliberately_ignored(self) -> None:
        for result in (0, 1, 0x80000000, 0xFFFFFFFF):
            with self.subTest(result=result):
                self.reset_fixture()
                self.set_result(result)
                self.assertIsNone(self.callback(0x20000000, 7))
                self.assertEqual(self.uint("calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0f4f59a07006e31cd1d34f41035785a91cee68337ea7d32a798d72741a1685df",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "4a246abe2c2e16a2d8388a9cc142a12c8645be6d32df92ce5dea7daffc1f3d2f",
        )


if __name__ == "__main__":
    unittest.main()
