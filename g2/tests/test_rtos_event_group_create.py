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
SOURCE = COMPONENT_ROOT / "rtos_event_group_create.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "rtos_event_group_create_host.c"
)


class RtosEventGroupCreateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "rtos_event_group_create.dylib"
            if sys.platform == "darwin"
            else "rtos_event_group_create.so"
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
        cls.reset_fixture = cls.loaded.open_cfw_test_rtos_event_group_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_object_size = (
            cls.loaded.open_cfw_test_rtos_event_group_set_object_size
        )
        cls.set_object_size.argtypes = [ctypes.c_uint]
        cls.set_object_size.restype = None
        cls.set_allocate_result = (
            cls.loaded.open_cfw_test_rtos_event_group_set_allocate_result
        )
        cls.set_allocate_result.argtypes = [ctypes.c_size_t]
        cls.set_allocate_result.restype = None
        cls.static_create = (
            cls.loaded.open_cfw_rtos_event_group_static_create
        )
        cls.static_create.argtypes = [ctypes.c_void_p]
        cls.static_create.restype = ctypes.c_void_p
        cls.dynamic_create = (
            cls.loaded.open_cfw_rtos_event_group_dynamic_create
        )
        cls.dynamic_create.argtypes = []
        cls.dynamic_create.restype = ctypes.c_void_p
        cls.object = (ctypes.c_ubyte * 32).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_object",
        )
        cls.object_address = ctypes.addressof(cls.object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def uint(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_{suffix}",
        )

    @classmethod
    def uintptr(cls, suffix: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(
            cls.loaded,
            f"open_cfw_test_rtos_event_group_{suffix}",
        )

    @classmethod
    def events(cls) -> list[int]:
        count = cls.uint("event_count").value
        values = (ctypes.c_uint * 16).in_dll(
            cls.loaded,
            "open_cfw_test_rtos_event_group_events",
        )
        return list(values)[:count]

    def test_static_create_initializes_exact_fields_in_stock_order(
        self,
    ) -> None:
        result = self.static_create(self.object_address)
        self.assertEqual(result, self.object_address)
        self.assertEqual(self.events(), [20, 30, 40, 50])
        self.assertEqual(bytes(self.object[:4]), b"\x00\x00\x00\x00")
        self.assertEqual(bytes(self.object[4:28]), b"\xA5" * 24)
        self.assertEqual(self.object[28], 1)
        self.assertEqual(bytes(self.object[29:32]), b"\xA5" * 3)

    def test_static_create_null_buffer_fail_stops_before_size_read(
        self,
    ) -> None:
        self.assertIsNone(self.static_create(None))
        self.assertEqual(self.events(), [10])
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("size_reads").value, 0)
        self.assertEqual(self.uint("bits_writes").value, 0)
        self.assertEqual(self.uint("list_initializes").value, 0)
        self.assertEqual(self.uint("static_writes").value, 0)

    def test_static_create_rejects_an_incompatible_object_size(
        self,
    ) -> None:
        self.set_object_size(31)
        self.assertIsNone(self.static_create(self.object_address))
        self.assertEqual(self.events(), [20, 10])
        self.assertEqual(self.uint("size_reads").value, 1)
        self.assertEqual(self.uint("fail_stop_calls").value, 1)
        self.assertEqual(self.uint("bits_writes").value, 0)
        self.assertEqual(bytes(self.object), b"\xA5" * 32)

    def test_static_create_uses_exact_object_and_field_addresses(
        self,
    ) -> None:
        self.static_create(self.object_address)
        self.assertEqual(
            self.uintptr("last_bits_group").value,
            self.object_address,
        )
        self.assertEqual(
            self.uintptr("last_list").value,
            self.object_address + 4,
        )
        self.assertEqual(
            self.uintptr("last_static_group").value,
            self.object_address,
        )
        self.assertEqual(self.uint("last_bits").value, 0)
        self.assertEqual(self.uint("last_static").value, 1)

    def test_dynamic_create_allocates_and_initializes_a_dynamic_object(
        self,
    ) -> None:
        self.set_allocate_result(self.object_address)
        result = self.dynamic_create()
        self.assertEqual(result, self.object_address)
        self.assertEqual(self.events(), [60, 30, 40, 50])
        self.assertEqual(self.uint("allocate_calls").value, 1)
        self.assertEqual(self.uint("allocate_size").value, 32)
        self.assertEqual(self.uint("size_reads").value, 0)
        self.assertEqual(bytes(self.object[:4]), b"\x00\x00\x00\x00")
        self.assertEqual(self.object[28], 0)
        self.assertEqual(self.uint("last_static").value, 0)

    def test_dynamic_create_null_allocation_suppresses_initialization(
        self,
    ) -> None:
        self.assertIsNone(self.dynamic_create())
        self.assertEqual(self.events(), [60])
        self.assertEqual(self.uint("allocate_calls").value, 1)
        self.assertEqual(self.uint("allocate_size").value, 32)
        self.assertEqual(self.uint("bits_writes").value, 0)
        self.assertEqual(self.uint("list_initializes").value, 0)
        self.assertEqual(self.uint("static_writes").value, 0)
        self.assertEqual(bytes(self.object), b"\xA5" * 32)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "de3435d6609f003fddaff01724fcbed52d1d6586869fb9199b051215b004d880",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "b94bc55d6863a380226ef6b1bb3025e6437df2d24ce8e5a1283e8babbdfe7889",
        )


if __name__ == "__main__":
    unittest.main()
