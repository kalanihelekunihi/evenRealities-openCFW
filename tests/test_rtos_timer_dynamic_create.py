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
SOURCE = COMPONENT_ROOT / "rtos_timer_dynamic_create.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_dynamic_create_host.c"
)


class RtosTimerDynamicCreateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_dynamic_create.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_dynamic_create.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_dynamic_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.create = cls.loaded.open_cfw_rtos_timer_dynamic_create
        cls.create.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        cls.create.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_dynamic_{suffix}",
        )

    @classmethod
    def uintptr_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_size_t]:
        return (ctypes.c_size_t * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_dynamic_{suffix}",
        )

    @classmethod
    def uint_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_dynamic_{suffix}",
        )

    @classmethod
    def byte_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_dynamic_{suffix}",
        )

    @classmethod
    def object_address(cls) -> int:
        return ctypes.addressof(cls.byte_array("object", 44))

    def test_allocation_failure_returns_null_without_initialization(
        self,
    ) -> None:
        self.assertIsNone(self.create(1, 2, 3, 4, 5))
        self.assertEqual(self.uint("allocate_calls").value, 1)
        self.assertEqual(self.uint("allocate_size").value, 44)
        self.assertEqual(self.uint("initialize_calls").value, 0)
        self.assertEqual(
            list(self.uint_array("events", 8))[:1],
            [1],
        )
        self.assertEqual(
            bytes(self.byte_array("object", 44)),
            bytes([0xA5]) * 44,
        )

    def test_success_clears_ownership_byte_before_initialization(self) -> None:
        self.uint("enabled").value = 1
        self.assertEqual(self.create(1, 2, 3, 4, 5), self.object_address())
        self.assertEqual(
            list(self.uint_array("events", 8))[:2],
            [1, 2],
        )
        self.assertEqual(self.uint("byte40_at_initialize").value, 0)
        expected = bytearray([0xA5] * 44)
        expected[40] = 0
        self.assertEqual(
            bytes(self.byte_array("object", 44)),
            bytes(expected),
        )

    def test_success_forwards_exact_six_argument_initializer_abi(
        self,
    ) -> None:
        self.uint("enabled").value = 1
        self.create(
            0x11111111,
            0x22222222,
            0x33333333,
            0x44444444,
            0x55555555,
        )
        self.assertEqual(
            list(self.uintptr_array("initialize_fields", 6)),
            [
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0x55555555,
                self.object_address(),
            ],
        )

    def test_full_width_period_and_periodic_values_are_preserved(self) -> None:
        self.uint("enabled").value = 1
        self.create(0, 0xFFFFFFFF, 0x80000004, 0, 0)
        fields = self.uintptr_array("initialize_fields", 6)
        self.assertEqual(fields[1:3], [0xFFFFFFFF, 0x80000004])

    def test_return_is_the_allocated_object(self) -> None:
        self.uint("enabled").value = 1
        result = self.create(0, 0, 0, 0, 0)
        self.assertEqual(result, self.object_address())
        self.assertEqual(self.uint("allocate_calls").value, 1)
        self.assertEqual(self.uint("initialize_calls").value, 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c970ffa4af1571dfde8f17a00ee8d096719287ad374b155dca5da0f32e9dcdda",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "1be7144d037e1ab805c9e6665d31e83494bbd9015c5c354608b561a68711b52b",
        )


if __name__ == "__main__":
    unittest.main()
