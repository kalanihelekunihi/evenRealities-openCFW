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
SOURCE = COMPONENT_ROOT / "mram_update_record_timestamp.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_update_record_timestamp_host.c"
)
CAPTURE_COUNT = 64
CAPTURE_WIDTH = 9


class MramUpdateRecordTimestampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_update_record_timestamp.dylib"
            if sys.platform == "darwin"
            else "mram_update_record_timestamp.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_timestamp_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.update = cls.loaded.open_cfw_mram_update_record_timestamp
        cls.update.argtypes = [ctypes.c_void_p]
        cls.update.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_size_t:
        return ctypes.c_size_t.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_size_t * count).in_dll(self.loaded, name)

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_timestamp_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_timestamp_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def log_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_timestamp_log_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_timestamp_logs",
            CAPTURE_COUNT * CAPTURE_WIDTH,
        )
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    def trace_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_timestamp_trace_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_timestamp_traces",
            CAPTURE_COUNT * CAPTURE_WIDTH,
        )
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    @staticmethod
    def timestamp(record: ctypes.Array) -> int:
        return int.from_bytes(bytes(record[0xC4:0xC8]), "little")

    def test_null_record_returns_without_side_effects(self) -> None:
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 12

        self.update(None)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_timestamp_counter"
            ).value,
            12,
        )
        self.assertEqual(self.order(), [])

    def test_increments_stores_updates_then_verifies(self) -> None:
        record = (ctypes.c_ubyte * 200)()
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 0x12345677
        self.word(
            "open_cfw_test_mram_timestamp_level_default"
        ).value = 7
        self.word(
            "open_cfw_test_mram_timestamp_update_result"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_timestamp_verify_result"
        ).value = 0

        self.update(record)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_timestamp_counter"
            ).value,
            0x12345678,
        )
        self.assertEqual(self.timestamp(record), 0x12345678)
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_timestamp_update_record"
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_timestamp_verify_record"
            ).value,
            ctypes.addressof(record),
        )
        self.assertEqual(self.order()[-2:], [5, 6])
        self.assertEqual(
            [item[4] for item in self.log_records()],
            [0x818],
        )
        self.assertEqual(self.log_records()[0][7], 0x12345678)
        self.assertEqual(self.trace_records()[0][4], 0x12345678)

    def test_overflow_diagnostic_precedes_retained_reset(self) -> None:
        record = (ctypes.c_ubyte * 200)()
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_timestamp_reset_value"
        ).value = 41
        self.word(
            "open_cfw_test_mram_timestamp_level_default"
        ).value = 7

        self.update(record)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_timestamp_reset_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_timestamp_counter"
            ).value,
            42,
        )
        self.assertEqual(self.timestamp(record), 42)
        self.assertEqual(
            [item[4] for item in self.log_records()],
            [0x813, 0x818],
        )
        self.assertEqual(
            self.order(),
            [1, 2, 1, 3, 4, 1, 2, 1, 3, 5, 6],
        )

    def test_retained_reset_result_controls_wrapping_increment(self) -> None:
        record = (ctypes.c_ubyte * 200)()
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_timestamp_reset_value"
        ).value = 0xFFFFFFFF

        self.update(record)

        self.assertEqual(
            self.word(
                "open_cfw_test_mram_timestamp_counter"
            ).value,
            0,
        )
        self.assertEqual(self.timestamp(record), 0)
        self.assertEqual(self.order(), [1, 1, 1, 4, 1, 1, 1, 5, 6])

    def test_diagnostic_metadata_and_independent_gates(self) -> None:
        record = (ctypes.c_ubyte * 200)()
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_timestamp_reset_value"
        ).value = 9
        self.word(
            "open_cfw_test_mram_timestamp_level_default"
        ).value = 2

        self.update(record)

        self.assertEqual(
            self.log_records()[0][:7],
            [
                2,
                0x0078A0D0,
                0x006D84BC,
                0x0076944C,
                0x813,
                0x006DF6B8,
                0,
            ],
        )
        self.assertEqual(
            self.log_records()[1][:8],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x0076944C,
                0x818,
                0x0071C188,
                1,
                10,
            ],
        )
        self.assertEqual(self.trace_records(), [])

        self.reset()
        self.word(
            "open_cfw_test_mram_timestamp_counter"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_timestamp_reset_value"
        ).value = 9
        self.word(
            "open_cfw_test_mram_timestamp_level_default"
        ).value = 1
        self.update(record)
        self.assertEqual(self.log_records(), [])
        self.assertEqual(
            [item[:4] for item in self.trace_records()],
            [
                [0x08000000, 0x006D8524, 0x006D8524, 0],
                [0x10400000, 0x00709524, 0x00709524, 1],
            ],
        )
        self.assertEqual(self.trace_records()[1][4], 10)

        self.reset()
        self.word(
            "open_cfw_test_mram_timestamp_level_default"
        ).value = 4
        self.update(record)
        self.assertEqual(self.log_records(), [])
        self.assertEqual(len(self.trace_records()), 1)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "04cbbb6e75ef00fd665a73e451407586671f6ae6c037bb275677652385507736",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "aa1632a7ab22c1b0d9a55c164f264756848f426ae680d2b143b36c874625c4bf",
        )


if __name__ == "__main__":
    unittest.main()
