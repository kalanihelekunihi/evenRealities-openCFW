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
SOURCE = COMPONENT_ROOT / "mram_allocate_record.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_allocate_record_host.c"
)
CAPTURE_COUNT = 32
CAPTURE_WIDTH = 12
RECORD_SIZE = 200
RECORD_COUNT = 10


class MramAllocateRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_allocate_record.dylib"
            if sys.platform == "darwin"
            else "mram_allocate_record.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_allocate_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.allocate = cls.loaded.open_cfw_mram_allocate_record
        cls.allocate.argtypes = [
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.allocate.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_allocate_records",
        )
        self.order = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_allocate_order",
        )
        self.levels = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_allocate_levels",
        )
        self.logs = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_allocate_logs",
        )
        self.traces = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_allocate_traces",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def record_address(self, index: int) -> int:
        return ctypes.addressof(self.records) + index * RECORD_SIZE

    def set_active(self, index: int, active: int = 1) -> None:
        self.records[index * RECORD_SIZE + 0x2F] = active

    def set_levels(self, values: list[int]) -> None:
        for index, value in enumerate(values):
            self.levels[index] = value
        self.word(
            "open_cfw_test_mram_allocate_level_count"
        ).value = len(values)

    def captured(
        self,
        values: ctypes.Array[ctypes.c_size_t],
        count_name: str,
    ) -> list[list[int]]:
        count = self.word(count_name).value
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    def test_allocates_first_free_record_and_initializes_in_stock_order(
        self,
    ) -> None:
        for index in range(2):
            self.set_active(index)
        start = 2 * RECORD_SIZE
        for offset in range(RECORD_SIZE):
            self.records[start + offset] = 0xFF
        self.records[start + 0x2F] = 0
        initial_value = ctypes.c_uint(0x12345678)
        self.word(
            "open_cfw_test_mram_allocate_map_owner_result"
        ).value = 0x34
        self.word("open_cfw_test_mram_allocate_counter").value = 41

        result = self.allocate(
            0xAB,
            ctypes.byref(initial_value),
            0x56,
            0xDEADBEEF,
        )

        self.assertEqual(result, self.record_address(2))
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_allocate_order_count"
                ).value
            ],
            [1, 5, 6, 7],
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_allocate_zero_record"
            ).value,
            result,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_allocate_zero_size").value,
            RECORD_SIZE,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_allocate_initialize_value"
            ).value,
            ctypes.addressof(initial_value),
        )
        expected = bytearray(RECORD_SIZE)
        expected[0x2F] = 1
        expected[6] = 0x34
        expected[7] = 0xA5
        expected[0xC3] = 0x56
        expected[0xC4:0xC8] = (42).to_bytes(4, "little")
        self.assertEqual(
            bytes(self.records[start:start + RECORD_SIZE]),
            bytes(expected),
        )

    def test_owner_and_type_are_truncated_and_counter_wraps(self) -> None:
        initial_value = ctypes.c_uint(7)
        self.word(
            "open_cfw_test_mram_allocate_map_owner_result"
        ).value = 0x1234
        self.word("open_cfw_test_mram_allocate_counter").value = 0xFFFFFFFF

        result = self.allocate(
            0x123456AB,
            ctypes.byref(initial_value),
            0xCAFEBE7E,
            0,
        )

        self.assertEqual(result, self.record_address(0))
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_allocate_count_type_argument"
            ).value,
            0x7E,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_allocate_map_owner_argument"
            ).value,
            0xAB,
        )
        self.assertEqual(self.records[6], 0x34)
        self.assertEqual(self.records[0xC3], 0x7E)
        self.assertEqual(
            ctypes.c_uint.from_buffer(self.records, 0xC4).value,
            0,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_allocate_counter").value,
            0,
        )

    def test_type_limit_releases_deactivates_and_reuses_oldest(self) -> None:
        for index in range(RECORD_COUNT):
            self.set_active(index)
        oldest = 4
        base = oldest * RECORD_SIZE
        self.records[base + 6] = 0x9A
        self.records[base + 0x30] = 1
        self.word("open_cfw_test_mram_allocate_count_result").value = 5
        self.pointer(
            "open_cfw_test_mram_allocate_oldest_result"
        ).value = self.record_address(oldest)
        self.word(
            "open_cfw_test_mram_allocate_map_owner_result"
        ).value = 0x22

        result = self.allocate(3, None, 0x12345644, 0)

        self.assertEqual(result, self.record_address(oldest))
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_allocate_order_count"
                ).value
            ],
            [1, 2, 3, 4, 5, 6, 7],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_allocate_oldest_type_argument"
            ).value,
            0x44,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_allocate_release_record"
            ).value,
            self.record_address(oldest),
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_allocate_release_owner"
            ).value,
            0x9A,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_allocate_release_flags"
            ).value,
            0,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_allocate_deactivate_record"
            ).value,
            self.record_address(oldest),
        )

    def test_missing_oldest_still_uses_an_existing_free_slot(self) -> None:
        for index in range(3):
            self.set_active(index)
        self.word("open_cfw_test_mram_allocate_count_result").value = 6

        result = self.allocate(0, None, 1, 0)

        self.assertEqual(result, self.record_address(3))
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_allocate_order_count"
                ).value
            ],
            [1, 2, 5, 6, 7],
        )

    def test_full_table_returns_null_without_mutating_records(self) -> None:
        for index in range(RECORD_COUNT):
            self.set_active(index)
        before = bytes(self.records)

        result = self.allocate(1, None, 2, 3)

        self.assertIsNone(result)
        self.assertEqual(bytes(self.records), before)
        self.assertEqual(
            list(self.order)[
                :self.word(
                    "open_cfw_test_mram_allocate_order_count"
                ).value
            ],
            [1],
        )

    def test_all_enabled_diagnostics_match_stock_metadata(self) -> None:
        for type_value, expected_label in (
            (0, 0x0078CA54),
            (0x12345678, 0x0078CA4C),
        ):
            with self.subTest(type_value=type_value):
                self.reset()
                for index in range(RECORD_COUNT):
                    self.set_active(index)
                self.word(
                    "open_cfw_test_mram_allocate_count_result"
                ).value = 5
                self.set_levels([7] * CAPTURE_COUNT)

                result = self.allocate(
                    1,
                    None,
                    type_value,
                    0xAABBCCDD,
                )

                self.assertIsNone(result)
                logs = self.captured(
                    self.logs,
                    "open_cfw_test_mram_allocate_log_count",
                )
                traces = self.captured(
                    self.traces,
                    "open_cfw_test_mram_allocate_trace_count",
                )
                self.assertEqual(
                    [row[:8] for row in logs],
                    [
                        [
                            4,
                            0x0078A0D0,
                            0x006D84BC,
                            0x00784F80,
                            0x396,
                            0x0071BFC8,
                            expected_label,
                            0xAABBCCDD,
                        ],
                        [
                            4,
                            0x0078A0D0,
                            0x006D84BC,
                            0x00784F80,
                            0x3B3,
                            0x00709264,
                            0,
                            0,
                        ],
                    ],
                )
                self.assertEqual(
                    [row[:4] for row in traces],
                    [
                        [
                            0x10400000,
                            0x007002C0,
                            0x007002C0,
                            expected_label,
                        ],
                        [
                            0x10000000,
                            0x006F1930,
                            0x006F1930,
                            0,
                        ],
                    ],
                )

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "68ce49559b76a86ba3218a0146044af897ce4dc3eed4ce51d0eda29dfcf236dd",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "7967e6c1fe37d7f1d64016618da7afaeb2668138d7d5152d72180c3da8c898c4",
        )


if __name__ == "__main__":
    unittest.main()
