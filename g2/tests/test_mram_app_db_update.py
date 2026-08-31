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
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "mram_app_db_update_host.c"
SOURCE = COMPONENT_ROOT / "mram_app_db_update.c"


class MramAppDbUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_app_db_update.dylib"
            if sys.platform == "darwin"
            else "mram_app_db_update.so"
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
        cls.reset_function = cls.loaded.open_cfw_test_mram_db_reset
        cls.reset_function.argtypes = []
        cls.reset_function.restype = None
        cls.update_function = cls.loaded.open_cfw_mram_app_db_update
        cls.update_function.argtypes = [ctypes.c_void_p]
        cls.update_function.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_function()
        self.nvm = (ctypes.c_ubyte * 2560).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_nvm",
        )
        self.order = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_order",
        )
        self.cache_ranges = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_cache_ranges",
        )
        self.cache_all = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_cache_all",
        )
        self.compare_left = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_compare_left",
        )
        self.compare_right = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_compare_right",
        )
        self.compare_sizes = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_compare_sizes",
        )
        self.update_records = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_update_records",
        )
        self.update_indices = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_update_indices",
        )
        self.dump_records = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_dump_records",
        )
        self.dump_indices = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_dump_indices",
        )
        self.levels = (ctypes.c_uint * 512).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_levels",
        )
        self.log_records = (ctypes.c_size_t * (256 * 16)).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_log_records",
        )
        self.trace_records = (ctypes.c_size_t * (256 * 16)).in_dll(
            self.loaded,
            "open_cfw_test_mram_db_trace_records",
        )

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def input_record(
        self,
        identifier: tuple[int, int, int, int, int, int] = (
            1,
            2,
            3,
            4,
            5,
            6,
        ),
        *,
        record_type: int = 1,
        timestamp: int = 0xA1B2C3D4,
    ) -> ctypes.Array:
        record = (ctypes.c_ubyte * 200)()
        for index, value in enumerate(identifier):
            record[index] = value
        record[0xC3] = record_type
        self.set_u32(record, 0xC4, timestamp)
        return record

    @staticmethod
    def set_u32(storage: ctypes.Array, offset: int, value: int) -> None:
        for index in range(4):
            storage[offset + index] = (value >> (index * 8)) & 0xFF

    def record_pointer(self, index: int) -> int:
        return ctypes.addressof(self.nvm) + index * 0x100

    def configure_record(
        self,
        index: int,
        *,
        identifier: tuple[int, int, int, int, int, int] | None = None,
        flag_2f: int = 1,
        flag_30: int = 1,
        record_type: int = 0,
        timestamp: int = 0x1000,
    ) -> None:
        offset = index * 0x100
        if identifier is None:
            identifier = (0x20 + index, 1, 2, 3, 4, 5)
        for byte_index, value in enumerate(identifier):
            self.nvm[offset + byte_index] = value
        self.nvm[offset + 0x2F] = flag_2f
        self.nvm[offset + 0x30] = flag_30
        self.nvm[offset + 0xC3] = record_type
        self.set_u32(self.nvm, offset + 0xC4, timestamp)

    def fill_full_table(self) -> None:
        for index in range(10):
            self.configure_record(
                index,
                record_type=index & 1,
                timestamp=0x100 + index,
            )

    def operational_order(self) -> list[int]:
        return [
            value
            for value in list(self.order)[
                :self.word("open_cfw_test_mram_db_order_count").value
            ]
            if value in (1, 2, 3, 4)
        ]

    @staticmethod
    def captured(
        storage: ctypes.Array,
        count: int,
    ) -> list[list[int]]:
        return [
            list(storage[index * 16:(index + 1) * 16])
            for index in range(count)
        ]

    def enable_all_diagnostics(self) -> None:
        for index in range(512):
            self.levels[index] = 7
        self.word("open_cfw_test_mram_db_level_count").value = 512

    def assert_selected(
        self,
        record: ctypes.Array,
        index: int,
        *,
        dumps: list[int],
        cache_calls: int,
    ) -> None:
        self.assertEqual(
            (
                self.word("open_cfw_test_mram_db_update_calls").value,
                self.update_records[0],
                self.update_indices[0],
            ),
            (1, ctypes.addressof(record), index),
        )
        self.assertEqual(
            list(self.dump_indices)[:len(dumps)],
            dumps,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_db_dump_calls").value,
            len(dumps),
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_db_cache_calls").value,
            cache_calls,
        )
        self.assertEqual(list(self.cache_ranges)[:cache_calls], [0] * cache_calls)
        self.assertEqual(list(self.cache_all)[:cache_calls], [1] * cache_calls)

    def test_existing_identifier_uses_first_match(self) -> None:
        record = self.input_record()
        for index in range(3):
            self.configure_record(index)
        for index in (2, 7):
            self.configure_record(
                index,
                identifier=(1, 2, 3, 4, 5, 6),
            )

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            2,
            dumps=[2],
            cache_calls=1,
        )
        self.assertEqual(
            list(self.compare_left)[:3],
            [ctypes.addressof(record)] * 3,
        )
        self.assertEqual(
            list(self.compare_right)[:3],
            [self.record_pointer(index) for index in range(3)],
        )
        self.assertEqual(list(self.compare_sizes)[:3], [6, 6, 6])
        self.assertEqual(
            self.operational_order(),
            [1, 2, 2, 2, 3, 4],
        )

    def test_empty_slot_accepts_only_uniform_zero_or_erased_identifier(
        self,
    ) -> None:
        record = self.input_record()
        self.configure_record(
            0,
            identifier=(0, 0xFF, 0, 0xFF, 0, 0xFF),
        )
        erased = 0x100
        for index in range(6):
            self.nvm[erased + index] = 0xFF

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            1,
            dumps=[1],
            cache_calls=1,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_db_compare_calls").value,
            1,
        )
        self.assertEqual(self.compare_right[0], self.record_pointer(0))

    def test_direct_zero_flag_candidate_stops_dump_and_verifies(self) -> None:
        record = self.input_record()
        self.fill_full_table()
        self.configure_record(
            3,
            flag_2f=0,
            flag_30=0,
            timestamp=0x12345678,
        )
        self.word("open_cfw_test_mram_db_update_mode").value = 1

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            3,
            dumps=[0, 1, 2, 3],
            cache_calls=2,
        )
        self.assertEqual(
            list(self.dump_records)[:4],
            [self.record_pointer(index) for index in range(4)],
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_db_compare_calls").value,
            11,
        )
        self.assertEqual(
            (
                self.compare_left[10],
                self.compare_right[10],
                self.compare_sizes[10],
            ),
            (self.record_pointer(3), ctypes.addressof(record), 6),
        )
        self.assertEqual(
            self.operational_order(),
            [1] + [2] * 10 + [4] * 4 + [3, 1, 2],
        )

    def test_oldest_inactive_uses_strict_minimum_and_first_tie(self) -> None:
        record = self.input_record()
        self.fill_full_table()
        self.configure_record(
            2,
            flag_2f=1,
            flag_30=0,
            timestamp=3,
        )
        self.configure_record(
            5,
            flag_2f=1,
            flag_30=0,
            timestamp=3,
        )
        self.word("open_cfw_test_mram_db_update_mode").value = 1

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            2,
            dumps=list(range(10)),
            cache_calls=2,
        )

    def test_active_same_type_precedes_lower_timestamp_other_type(
        self,
    ) -> None:
        record = self.input_record(record_type=1)
        self.fill_full_table()
        for index in range(10):
            self.configure_record(
                index,
                record_type=0,
                timestamp=10 + index,
            )
        self.configure_record(4, record_type=1, timestamp=50)
        self.configure_record(6, record_type=1, timestamp=60)
        self.word("open_cfw_test_mram_db_update_mode").value = 1

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            4,
            dumps=list(range(10)),
            cache_calls=2,
        )

    def test_active_any_is_final_usable_fallback(self) -> None:
        record = self.input_record(record_type=1)
        self.fill_full_table()
        for index in range(10):
            self.configure_record(
                index,
                record_type=0,
                timestamp=100 + index,
            )
        self.configure_record(8, record_type=0, timestamp=2)
        self.word("open_cfw_test_mram_db_update_mode").value = 1

        self.assertEqual(self.update_function(record), 1)
        self.assert_selected(
            record,
            8,
            dumps=list(range(10)),
            cache_calls=2,
        )

    def test_no_candidate_returns_zero_without_programming(self) -> None:
        record = self.input_record()
        for index in range(10):
            self.configure_record(
                index,
                flag_2f=0,
                flag_30=1,
            )

        self.assertEqual(self.update_function(record), 0)
        self.assertEqual(
            (
                self.word("open_cfw_test_mram_db_update_calls").value,
                self.word("open_cfw_test_mram_db_dump_calls").value,
                self.word("open_cfw_test_mram_db_cache_calls").value,
                self.word("open_cfw_test_mram_db_compare_calls").value,
            ),
            (0, 10, 1, 10),
        )

    def test_verify_failure_is_reported_but_returns_success(self) -> None:
        record = self.input_record()
        self.fill_full_table()
        self.configure_record(
            3,
            flag_2f=0,
            flag_30=0,
            timestamp=0x12345678,
        )
        self.word("open_cfw_test_mram_db_update_mode").value = 2
        self.enable_all_diagnostics()

        self.assertEqual(self.update_function(record), 1)
        logs = self.captured(
            self.log_records,
            self.word("open_cfw_test_mram_db_log_count").value,
        )
        traces = self.captured(
            self.trace_records,
            self.word("open_cfw_test_mram_db_trace_count").value,
        )
        self.assertEqual(
            [entry[4] for entry in logs[-3:]],
            [0x291, 0x294, 0x297],
        )
        self.assertEqual(
            [entry[0] for entry in traces[-3:]],
            [0x04400000, 0x05800000, 0x05800000],
        )
        self.assertEqual(logs[-3][6], 3)
        self.assertEqual(logs[-2][6:12], [6, 5, 4, 3, 2, 1])
        self.assertEqual(
            logs[-1][6:12],
            [6, 5, 4, 3, 2, 0xFE],
        )

    def test_direct_candidate_emits_complete_diagnostic_abi(self) -> None:
        record = self.input_record()
        self.fill_full_table()
        self.configure_record(
            3,
            flag_2f=0,
            flag_30=0,
            timestamp=0x12345678,
        )
        self.word("open_cfw_test_mram_db_update_mode").value = 1
        self.enable_all_diagnostics()

        self.assertEqual(self.update_function(record), 1)
        logs = self.captured(self.log_records, 10)
        traces = self.captured(self.trace_records, 10)
        expected = [
            (4, 0x1BE, 0x0071258C, 0x10000000, 0x006F82DC, []),
            (
                4,
                0x1CE,
                0x006F8324,
                0x10C00000,
                0x006E6280,
                [0x007FF000, 0x100, 0x40],
            ),
            (2, 0x222, 0x006F1800, 0x08400000, 0x006E2388, [0x0078CA4C]),
            (4, 0x231, 0x00709164, 0x10400000, 0x006F83B4, [3]),
            (
                4,
                0x27C,
                0x007125C8,
                0x10800000,
                0x007001F4,
                [3, 0x12345678],
            ),
            (
                4,
                0x27F,
                0x00712604,
                0x11800000,
                0x006F83FC,
                [5, 4, 3, 2, 1, 0x23],
            ),
            (4, 0x282, 0x0074783C, 0x10400000, 0x00726D88, [3]),
            (
                4,
                0x284,
                0x007091A4,
                0x10800000,
                0x006F184C,
                [3 << 6, 3 << 8],
            ),
            (4, 0x285, 0x0071BF58, 0x10400000, 0x00700238, [3 << 6]),
            (
                4,
                0x28F,
                0x006D9F08,
                0x11C00000,
                0x006A6BD4,
                [6, 5, 4, 3, 2, 1, 3],
            ),
        ]
        self.assertEqual(
            (
                self.word("open_cfw_test_mram_db_log_count").value,
                self.word("open_cfw_test_mram_db_trace_count").value,
                self.word("open_cfw_test_mram_db_level_index").value,
            ),
            (10, 10, 20),
        )
        for index, (
            severity,
            line,
            log_identity,
            event,
            trace_identity,
            arguments,
        ) in enumerate(expected):
            self.assertEqual(
                logs[index][:6],
                [
                    severity,
                    0x0078A0D0,
                    0x006D84BC,
                    0x00784F70,
                    line,
                    log_identity,
                ],
            )
            self.assertEqual(
                logs[index][6:6 + len(arguments)],
                arguments,
            )
            self.assertEqual(
                traces[index][:3],
                [event, trace_identity, trace_identity],
            )
            self.assertEqual(
                traces[index][3:3 + len(arguments)],
                arguments,
            )

    def test_existing_empty_inactive_and_no_candidate_diagnostic_paths(
        self,
    ) -> None:
        scenarios = [
            ("existing", [0x1BE, 0x1CE, 0x1E8, 0x1ED]),
            ("empty", [0x1BE, 0x1CE, 0x20E, 0x213]),
            (
                "inactive",
                [
                    0x1BE,
                    0x1CE,
                    0x222,
                    0x249,
                    0x27C,
                    0x27F,
                    0x282,
                    0x284,
                    0x285,
                    0x28F,
                ],
            ),
            ("none", [0x1BE, 0x1CE, 0x222, 0x29C]),
        ]
        for name, expected_lines in scenarios:
            with self.subTest(name=name):
                self.reset_function()
                self.nvm = (ctypes.c_ubyte * 2560).in_dll(
                    self.loaded,
                    "open_cfw_test_mram_db_nvm",
                )
                self.enable_all_diagnostics()
                record = self.input_record()
                if name == "existing":
                    self.configure_record(
                        0,
                        identifier=(1, 2, 3, 4, 5, 6),
                    )
                elif name == "inactive":
                    self.fill_full_table()
                    self.configure_record(
                        2,
                        flag_2f=1,
                        flag_30=0,
                        timestamp=3,
                    )
                    self.word(
                        "open_cfw_test_mram_db_update_mode"
                    ).value = 1
                elif name == "none":
                    for index in range(10):
                        self.configure_record(
                            index,
                            flag_2f=0,
                            flag_30=1,
                        )

                self.update_function(record)
                count = self.word(
                    "open_cfw_test_mram_db_log_count"
                ).value
                logs = self.captured(self.log_records, count)
                self.assertEqual(
                    [entry[4] for entry in logs],
                    expected_lines,
                )
                if name in ("existing", "empty"):
                    self.assertEqual(logs[-2][6], 0)
                    self.assertEqual(logs[-1][6], 0)
                elif name == "inactive":
                    self.assertEqual(logs[3][6:8], [2, 3])
                else:
                    self.assertEqual(logs[-1][0], 1)

    def test_trace_bit_four_fallback_without_structured_logging(self) -> None:
        record = self.input_record()
        self.configure_record(
            0,
            identifier=(1, 2, 3, 4, 5, 6),
        )
        for diagnostic in range(4):
            offset = diagnostic * 3
            self.levels[offset] = 0
            self.levels[offset + 1] = 0
            self.levels[offset + 2] = 4
        self.word("open_cfw_test_mram_db_level_count").value = 12

        self.assertEqual(self.update_function(record), 1)
        self.assertEqual(
            (
                self.word("open_cfw_test_mram_db_level_index").value,
                self.word("open_cfw_test_mram_db_log_count").value,
                self.word("open_cfw_test_mram_db_trace_count").value,
            ),
            (12, 0, 4),
        )
        traces = self.captured(self.trace_records, 4)
        self.assertEqual(
            [(entry[0], entry[1]) for entry in traces],
            [
                (0x10000000, 0x006F82DC),
                (0x10C00000, 0x006E6280),
                (0x10400000, 0x006F836C),
                (0x10400000, 0x00751EA8),
            ],
        )

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "d54f0950c3da9af9b02c452fc128c1f63306930ecdd13f49d0e36dea08818b80",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "0bb3714476325ca5d7db75fb4113bde842e2703d7c61307b1f8b03d4ca6db9ef",
        )


if __name__ == "__main__":
    unittest.main()
