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
SOURCE = COMPONENT_ROOT / "mram_delete_all_records.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_delete_all_records_host.c"
)
CAPTURE_COUNT = 80
CAPTURE_WIDTH = 6
RECORD_COUNT = 10
RECORD_SIZE = 200


class MramDeleteAllRecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_delete_all_records.dylib"
            if sys.platform == "darwin"
            else "mram_delete_all_records.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_delete_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.delete = cls.loaded.open_cfw_mram_delete_all_records
        cls.delete.argtypes = []
        cls.delete.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_delete_records",
        )
        self.levels = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_delete_levels",
        )
        self.logs = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_delete_logs",
        )
        self.traces = (
            ctypes.c_size_t * (CAPTURE_COUNT * CAPTURE_WIDTH)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_delete_traces",
        )
        self.order = (ctypes.c_uint * CAPTURE_COUNT).in_dll(
            self.loaded,
            "open_cfw_test_mram_delete_order",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def set_levels(self, values: list[int]) -> None:
        for index, value in enumerate(values):
            self.levels[index] = value
        self.word("open_cfw_test_mram_delete_level_count").value = len(
            values
        )

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

    def test_clears_only_address_and_validity_fields_before_persistence(
        self,
    ) -> None:
        before = bytearray(RECORD_COUNT * RECORD_SIZE)
        for index in range(len(before)):
            before[index] = (index * 37 + 11) & 0xFF
            self.records[index] = before[index]

        self.delete()

        for record_index in range(RECORD_COUNT):
            base = record_index * RECORD_SIZE
            for offset in range(RECORD_SIZE):
                expected = (
                    0
                    if offset < 6 or offset in (0x2F, 0x30)
                    else before[base + offset]
                )
                self.assertEqual(
                    self.records[base + offset],
                    expected,
                    (record_index, offset),
                )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_clear_count"
            ).value,
            60,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_flags_were_clear"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_program_calls"
            ).value,
            1,
        )
        expected_order = [
            record_index * 10 + address_index + 1
            for record_index in range(RECORD_COUNT)
            for address_index in range(6)
        ] + [1000]
        self.assertEqual(
            list(self.order)[:len(expected_order)],
            expected_order,
        )

    def test_structured_and_trace_diagnostics_match_stock_metadata(
        self,
    ) -> None:
        self.set_levels([3, 3])

        self.delete()

        self.assertEqual(
            self.captured(
                self.logs,
                "open_cfw_test_mram_delete_log_count",
            ),
            [[
                4,
                0x0078A0D0,
                0x006D84BC,
                0x00775134,
                0x45A,
                0x0077514C,
            ]],
        )
        self.assertEqual(
            self.captured(
                self.traces,
                "open_cfw_test_mram_delete_trace_count",
            ),
            [[0x10000000, 0x00751ECC, 0x00751ECC, 0, 0, 0]],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_level_index"
            ).value,
            2,
        )

    def test_structured_gate_does_not_imply_trace(self) -> None:
        self.set_levels([2, 2, 2])

        self.delete()

        self.assertEqual(
            self.word("open_cfw_test_mram_delete_log_count").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_delete_trace_count").value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_level_index"
            ).value,
            3,
        )

    def test_trace_fallback_uses_second_level_read(self) -> None:
        self.set_levels([0, 0, 4])

        self.delete()

        self.assertEqual(
            self.word("open_cfw_test_mram_delete_log_count").value,
            0,
        )
        self.assertEqual(
            self.captured(
                self.traces,
                "open_cfw_test_mram_delete_trace_count",
            ),
            [[0x10000000, 0x00751ECC, 0x00751ECC, 0, 0, 0]],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_delete_level_index"
            ).value,
            3,
        )

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "b4bba63529a4900499f9d446b7663c4df4ae28d520810ea03bbd602538e7cdd5",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "ea0cb543f21337ba661c61a68a62623843a01d9eec34b0b189d2ad08b2881b1f",
        )


if __name__ == "__main__":
    unittest.main()
