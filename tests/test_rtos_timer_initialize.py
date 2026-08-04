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
SOURCE = COMPONENT_ROOT / "rtos_timer_initialize.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_timer_initialize_host.c"
)


class RtosTimerInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_timer_initialize.dylib"
            if sys.platform == "darwin"
            else "rtos_timer_initialize.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_timer_initialize_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.initialize = cls.loaded.open_cfw_rtos_timer_initialize
        cls.initialize.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_initialize_{suffix}",
        )

    @classmethod
    def uint_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_uint]:
        return (ctypes.c_uint * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_initialize_{suffix}",
        )

    @classmethod
    def byte_array(
        cls,
        suffix: str,
        length: int,
    ) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * length).in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_timer_initialize_{suffix}",
        )

    @classmethod
    def object_address(cls) -> int:
        return ctypes.addressof(cls.byte_array("object", 44))

    def initialize_object(
        self,
        *,
        name: int = 0x11111111,
        period_ticks: int = 0x22222222,
        periodic: int = 0,
        callback_context: int = 0x33333333,
        callback: int = 0x44444444,
    ) -> None:
        self.initialize(
            name,
            period_ticks,
            periodic,
            callback_context,
            callback,
            self.object_address(),
        )

    def test_zero_period_fail_stops_before_runtime_or_object_writes(
        self,
    ) -> None:
        self.initialize_object(period_ticks=0, periodic=1)
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("runtime_calls").value, 0)
        self.assertEqual(self.uint("store_calls").value, 0)
        self.assertEqual(self.uint("or_calls").value, 0)
        self.assertEqual(list(self.uint_array("events", 16))[:1], [40])
        self.assertEqual(
            bytes(self.byte_array("object", 44)),
            bytes([0xA5]) * 44,
        )

    def test_runtime_initialization_precedes_every_object_write(self) -> None:
        self.initialize_object(periodic=1)
        self.assertEqual(self.uint("runtime_calls").value, 1)
        self.assertEqual(
            bytes(self.byte_array("runtime_snapshot", 44)),
            bytes([0xA5]) * 44,
        )
        self.assertEqual(
            list(self.uint_array("events", 16))[:7],
            [1, 10, 11, 12, 13, 14, 30],
        )

    def test_exact_field_store_order_offsets_and_values(self) -> None:
        self.initialize_object()
        self.assertEqual(
            list(self.uint_array("store_offsets", 8))[:5],
            [0x00, 0x18, 0x1C, 0x20, 0x14],
        )
        self.assertEqual(
            list(self.uint_array("store_values", 8))[:5],
            [
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0,
            ],
        )

    def test_nonperiodic_object_preserves_existing_flags_byte(self) -> None:
        object_bytes = self.byte_array("object", 44)
        object_bytes[0x28] = 2
        self.initialize_object(periodic=0)
        self.assertEqual(object_bytes[0x28], 2)
        self.assertEqual(self.uint("or_calls").value, 0)

    def test_periodic_object_ors_bit_two_after_all_word_stores(self) -> None:
        object_bytes = self.byte_array("object", 44)
        object_bytes[0x28] = 0xA2
        self.initialize_object(periodic=0xFFFFFFFF)
        self.assertEqual(object_bytes[0x28], 0xA6)
        self.assertEqual(self.uint("or_calls").value, 1)
        self.assertEqual(self.uint("or_offset").value, 0x28)
        self.assertEqual(self.uint("or_mask").value, 4)
        self.assertEqual(list(self.uint_array("events", 16))[6], 30)

    def test_pointer_fields_use_the_32_bit_firmware_abi(self) -> None:
        self.initialize_object(
            name=0x12345678ABCDEF01,
            callback_context=0x8765432112345678,
            callback=0xFEDCBA9876543210,
        )
        self.assertEqual(
            list(self.uint_array("store_values", 8))[:5],
            [
                0xABCDEF01,
                0x22222222,
                0x12345678,
                0x76543210,
                0,
            ],
        )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c0d1ec899b6c64da0ac3ad6cb53a5aa53a136ed30f8d6e69f21666915a258e11",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "14c679a7b1b8a5a2c47ebdf6faada91bdbca4b598c127213e746be3f3e5a6046",
        )


if __name__ == "__main__":
    unittest.main()
