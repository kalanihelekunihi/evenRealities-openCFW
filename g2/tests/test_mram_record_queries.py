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
SOURCE = COMPONENT_ROOT / "mram_record_queries.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_record_queries_host.c"
)
RECORD_SIZE = 200
RECORD_COUNT = 10


class MramRecordQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_record_queries.dylib"
            if sys.platform == "darwin"
            else "mram_record_queries.so"
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
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_mram_query_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.is_active = cls.loaded.open_cfw_mram_record_is_active
        cls.is_active.argtypes = [ctypes.c_void_p]
        cls.is_active.restype = ctypes.c_uint
        cls.has_untyped = cls.loaded.open_cfw_mram_has_untyped_record
        cls.has_untyped.argtypes = []
        cls.has_untyped.restype = ctypes.c_uint
        cls.next_active = cls.loaded.open_cfw_mram_next_active_record
        cls.next_active.argtypes = [ctypes.c_void_p]
        cls.next_active.restype = ctypes.c_void_p
        cls.count_type = cls.loaded.open_cfw_mram_count_active_type
        cls.count_type.argtypes = [ctypes.c_uint]
        cls.count_type.restype = ctypes.c_uint
        cls.oldest_type = cls.loaded.open_cfw_mram_oldest_active_type
        cls.oldest_type.argtypes = [ctypes.c_uint]
        cls.oldest_type.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_SIZE * RECORD_COUNT)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_query_records",
        )
        self.base = ctypes.addressof(self.records)

    def pointer(self, index: int) -> int:
        return self.base + index * RECORD_SIZE

    def set_byte(self, index: int, offset: int, value: int) -> None:
        self.records[index * RECORD_SIZE + offset] = value

    def set_timestamp(self, index: int, value: int) -> None:
        ctypes.c_uint.from_buffer(
            self.records,
            index * RECORD_SIZE + 0xC4,
        ).value = value

    def test_active_membership_requires_both_flags_and_pointer_identity(
        self,
    ) -> None:
        self.set_byte(3, 0x2F, 1)
        self.set_byte(3, 0x30, 2)
        external = (ctypes.c_ubyte * RECORD_SIZE)()
        external[0x2F] = 1
        external[0x30] = 2

        self.assertEqual(self.is_active(self.pointer(3)), 1)
        self.assertEqual(self.is_active(external), 0)
        self.set_byte(3, 0x30, 0)
        self.assertEqual(self.is_active(self.pointer(3)), 0)
        self.set_byte(3, 0x30, 1)
        self.set_byte(3, 0x2F, 0)
        self.assertEqual(self.is_active(self.pointer(3)), 0)

    def test_untyped_query_requires_only_allocated_flag_and_zero_type(
        self,
    ) -> None:
        self.set_byte(4, 0x2F, 1)
        self.set_byte(4, 0x30, 0)
        self.set_byte(4, 0xC3, 9)
        self.assertEqual(self.has_untyped(), 0)

        self.set_byte(4, 0xC3, 0)
        self.assertEqual(self.has_untyped(), 1)

        self.set_byte(4, 0x2F, 0)
        self.assertEqual(self.has_untyped(), 0)

    def test_next_active_traverses_from_base_or_after_input(self) -> None:
        for index in (0, 2, 9):
            self.set_byte(index, 0x2F, 1)
        self.set_byte(2, 0x30, 0)

        self.assertEqual(self.next_active(None), self.pointer(0))
        self.assertEqual(
            self.next_active(self.pointer(0)),
            self.pointer(2),
        )
        self.assertEqual(
            self.next_active(self.pointer(2)),
            self.pointer(9),
        )
        self.assertIsNone(self.next_active(self.pointer(9)))

    def test_count_active_type_truncates_type_and_ignores_confirmation(
        self,
    ) -> None:
        for index, confirmation in ((1, 0), (3, 1), (8, 0xFF)):
            self.set_byte(index, 0x2F, 1)
            self.set_byte(index, 0x30, confirmation)
            self.set_byte(index, 0xC3, 0xAB)
        self.set_byte(5, 0x2F, 0)
        self.set_byte(5, 0xC3, 0xAB)
        self.set_byte(6, 0x2F, 1)
        self.set_byte(6, 0xC3, 0xAC)

        self.assertEqual(self.count_type(0x123456AB), 3)
        self.assertEqual(self.count_type(0xAC), 1)

    def test_oldest_active_type_uses_strict_first_minimum(self) -> None:
        for index, timestamp in ((2, 100), (3, 50), (4, 50)):
            self.set_byte(index, 0x2F, 1)
            self.set_byte(index, 0x30, 1)
            self.set_byte(index, 0xC3, 7)
            self.set_timestamp(index, timestamp)
        self.set_byte(1, 0x2F, 1)
        self.set_byte(1, 0x30, 0)
        self.set_byte(1, 0xC3, 7)
        self.set_timestamp(1, 1)

        self.assertEqual(self.oldest_type(0x107), self.pointer(3))

    def test_maximum_timestamp_is_not_selected(self) -> None:
        self.set_byte(7, 0x2F, 1)
        self.set_byte(7, 0x30, 1)
        self.set_byte(7, 0xC3, 4)
        self.set_timestamp(7, 0xFFFFFFFF)

        self.assertIsNone(self.oldest_type(4))

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "e6fa3429391acf5b19927f5ad16863b616a55c8968dcbb6af68f26198a367176",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "dbde2191f138ca2c90f4b32cfaf128b57cff49e3df9548d49796316034f17d57",
        )


if __name__ == "__main__":
    unittest.main()
