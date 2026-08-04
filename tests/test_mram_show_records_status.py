from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mram_show_records_status.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_show_records_status_host.c"
)
RECORD_COUNT = 10
RECORD_STRIDE = 0x100
CAPTURE_COUNT = 128
CAPTURE_WIDTH = 14


class MramShowRecordsStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_show_records_status.dylib"
            if sys.platform == "darwin"
            else "mram_show_records_status.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_status_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.show = cls.loaded.open_cfw_mram_show_all_records_status
        cls.show.argtypes = []
        cls.show.restype = None

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

    def nvm(self) -> ctypes.Array:
        return (ctypes.c_ubyte * (RECORD_COUNT * RECORD_STRIDE)).in_dll(
            self.loaded,
            "open_cfw_test_mram_status_nvm",
        )

    def set_u32(self, index: int, offset: int, value: int) -> None:
        output = self.nvm()
        start = index * RECORD_STRIDE + offset
        output[start:start + 4] = value.to_bytes(4, "little")

    def configure_slot(
        self,
        index: int,
        *,
        valid: int,
        in_use: int,
        timestamp: int,
        key_mask: int = 0,
        address: bytes = b"\0\0\0\0\0\0",
        owner: int = 0,
    ) -> None:
        output = self.nvm()
        start = index * RECORD_STRIDE
        output[start:start + 6] = address
        output[start + 6] = owner
        output[start + 0x2E] = key_mask
        output[start + 0x2F] = in_use
        output[start + 0x30] = valid
        self.set_u32(index, 0xC4, timestamp)

    def configure_full_logging(self) -> None:
        self.word(
            "open_cfw_test_mram_status_level_default"
        ).value = 7

    def log_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_status_log_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_status_logs",
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
            "open_cfw_test_mram_status_trace_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_status_traces",
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

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_status_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_status_order",
                CAPTURE_COUNT,
            )[:count]
        )

    @staticmethod
    def arguments(record: list[int], trace: bool = False) -> list[int]:
        if trace:
            return record[4:4 + record[3]]
        return record[7:7 + record[6]]

    def test_initial_metadata_classification_and_cache_order(self) -> None:
        self.configure_full_logging()
        self.word(
            "open_cfw_test_mram_status_timestamp_counter"
        ).value = 0x12345678
        for index in range(RECORD_COUNT):
            self.configure_slot(
                index,
                valid=0,
                in_use=0,
                timestamp=0x100 + index,
            )
        self.configure_slot(1, valid=0, in_use=1, timestamp=0xAABBCCDD)
        self.configure_slot(2, valid=1, in_use=0, timestamp=0x01020304)

        self.show()

        logs = self.log_records()
        self.assertEqual(
            [record[4] for record in logs],
            [
                0x7D3, 0x7D4, 0x7D5,
                0x7F7, 0x7F4, 0x7F7,
                0x7F7, 0x7F7, 0x7F7, 0x7F7, 0x7F7, 0x7F7, 0x7F7,
                0x7FB, 0x800,
            ],
        )
        self.assertEqual(self.arguments(logs[1]), [10])
        self.assertEqual(self.arguments(logs[2]), [0x12345678])
        self.assertEqual(self.arguments(logs[3]), [0, 0x100])
        self.assertEqual(self.arguments(logs[4]), [1, 0xAABBCCDD])
        self.assertEqual(self.arguments(logs[5]), [2, 0x01020304])
        self.assertEqual(self.arguments(logs[-2]), [0, 10])
        self.assertEqual(
            self.order()[:13],
            [1, 2, 1, 3] * 3 + [4],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_cache_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_status_cache_range"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_cache_clean"
            ).value,
            1,
        )

    def test_active_record_arguments_and_oldest_newest(self) -> None:
        self.configure_full_logging()
        self.configure_slot(
            1,
            valid=1,
            in_use=1,
            timestamp=5,
            key_mask=0xA5,
            address=bytes.fromhex("102030405060"),
            owner=3,
        )
        self.configure_slot(
            4,
            valid=1,
            in_use=1,
            timestamp=9,
            key_mask=0x5A,
            address=bytes.fromhex("a1b2c3d4e5f6"),
            owner=2,
        )

        self.show()

        logs = self.log_records()
        summaries = [item for item in logs if item[4] == 0x7E4]
        devices = [item for item in logs if item[4] == 0x7E7]
        self.assertEqual(
            [self.arguments(item) for item in summaries],
            [[1, 5, 0xA5], [4, 9, 0x5A]],
        )
        self.assertEqual(
            [self.arguments(item) for item in devices],
            [
                [0x60, 0x50, 0x40, 0x30, 0x20, 0x10, 3],
                [0xF6, 0xE5, 0xD4, 0xC3, 0xB2, 0xA1, 2],
            ],
        )
        by_line = {item[4]: item for item in logs}
        self.assertEqual(self.arguments(by_line[0x7FB]), [2, 10])
        self.assertEqual(self.arguments(by_line[0x7FD]), [1, 5])
        self.assertEqual(self.arguments(by_line[0x7FE]), [4, 9])

    def test_strict_ties_and_extreme_timestamp_defaults(self) -> None:
        self.configure_full_logging()
        self.configure_slot(2, valid=1, in_use=1, timestamp=7)
        self.configure_slot(5, valid=1, in_use=1, timestamp=7)

        self.show()

        by_line = {item[4]: item for item in self.log_records()}
        self.assertEqual(self.arguments(by_line[0x7FD]), [2, 7])
        self.assertEqual(self.arguments(by_line[0x7FE]), [2, 7])

        self.reset()
        self.configure_full_logging()
        self.configure_slot(
            7,
            valid=1,
            in_use=1,
            timestamp=0xFFFFFFFF,
        )
        self.show()
        by_line = {item[4]: item for item in self.log_records()}
        self.assertEqual(
            self.arguments(by_line[0x7FD]),
            [0, 0xFFFFFFFF],
        )
        self.assertEqual(
            self.arguments(by_line[0x7FE]),
            [7, 0xFFFFFFFF],
        )

        self.reset()
        self.configure_full_logging()
        self.configure_slot(6, valid=1, in_use=1, timestamp=0)
        self.show()
        by_line = {item[4]: item for item in self.log_records()}
        self.assertEqual(self.arguments(by_line[0x7FD]), [6, 0])
        self.assertEqual(self.arguments(by_line[0x7FE]), [0, 0])

    def test_complete_diagnostic_metadata(self) -> None:
        self.configure_full_logging()
        self.configure_slot(0, valid=0, in_use=1, timestamp=11)
        self.configure_slot(
            1,
            valid=1,
            in_use=1,
            timestamp=22,
            key_mask=0xCC,
            address=bytes.fromhex("010203040506"),
            owner=4,
        )

        self.show()

        expected = {
            0x7D3: (0x00751F5C, 0x10000000, 0x00731964),
            0x7D4: (0x0077DDF8, 0x10400000, 0x0075DE70),
            0x7D5: (0x0075DE90, 0x10400000, 0x0073C140),
            0x7F4: (0x00726F28, 0x10800000, 0x007094A4),
            0x7F7: (0x00726F5C, 0x10800000, 0x007094E4),
            0x7E4: (0x007004E0, 0x10C00000, 0x006EB678),
            0x7E7: (0x00726EF4, 0x11C00000, 0x00709464),
            0x7FB: (0x0077517C, 0x10800000, 0x0075DEB0),
            0x7FD: (0x007478DC, 0x10800000, 0x00726F90),
            0x7FE: (0x00747904, 0x10800000, 0x00726FC4),
            0x800: (0x0074792C, 0x10000000, 0x00726FF8),
        }
        logs = self.log_records()
        traces = self.trace_records()
        for line, (structured, event, trace_identity) in expected.items():
            log = next(item for item in logs if item[4] == line)
            self.assertEqual(
                log[:6],
                [4, 0x0078A0D0, 0x006D84BC, 0x00769430, line, structured],
            )
            trace = next(
                item
                for item in traces
                if item[0] == event and item[1] == trace_identity
            )
            self.assertEqual(trace[1], trace[2])

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        self.word(
            "open_cfw_test_mram_status_level_default"
        ).value = 2
        self.show()
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_log_count"
            ).value,
            15,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_trace_count"
            ).value,
            0,
        )

        self.reset()
        self.word(
            "open_cfw_test_mram_status_level_default"
        ).value = 1
        self.show()
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_log_count"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_trace_count"
            ).value,
            15,
        )

        self.reset()
        self.word(
            "open_cfw_test_mram_status_level_default"
        ).value = 4
        self.show()
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_log_count"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_status_trace_count"
            ).value,
            15,
        )

    def test_randomized_model_matches_stock_selection(self) -> None:
        generator = random.Random(0x47BC30)

        for _ in range(500):
            self.reset()
            self.word(
                "open_cfw_test_mram_status_level_default"
            ).value = 2
            active: list[tuple[int, int]] = []
            expected_slot_lines: list[int] = []
            for index in range(RECORD_COUNT):
                valid = generator.randrange(2)
                in_use = generator.randrange(2)
                timestamp = generator.getrandbits(32)
                self.configure_slot(
                    index,
                    valid=valid,
                    in_use=in_use,
                    timestamp=timestamp,
                    key_mask=generator.getrandbits(8),
                    address=bytes(
                        generator.getrandbits(8) for _ in range(6)
                    ),
                    owner=generator.getrandbits(8),
                )
                if valid and in_use:
                    active.append((index, timestamp))
                    expected_slot_lines.extend([0x7E4, 0x7E7])
                elif in_use:
                    expected_slot_lines.append(0x7F4)
                else:
                    expected_slot_lines.append(0x7F7)

            self.show()

            logs = self.log_records()
            self.assertEqual(
                [item[4] for item in logs[3:3 + len(expected_slot_lines)]],
                expected_slot_lines,
            )
            by_line = {}
            for item in logs:
                by_line.setdefault(item[4], []).append(item)
            self.assertEqual(
                self.arguments(by_line[0x7FB][0]),
                [len(active), RECORD_COUNT],
            )
            if not active:
                self.assertNotIn(0x7FD, by_line)
                self.assertNotIn(0x7FE, by_line)
                continue

            oldest_timestamp = 0xFFFFFFFF
            newest_timestamp = 0
            oldest_index = 0
            newest_index = 0
            for index, timestamp in active:
                if timestamp < oldest_timestamp:
                    oldest_timestamp = timestamp
                    oldest_index = index
                if timestamp > newest_timestamp:
                    newest_timestamp = timestamp
                    newest_index = index
            self.assertEqual(
                self.arguments(by_line[0x7FD][0]),
                [oldest_index, oldest_timestamp],
            )
            self.assertEqual(
                self.arguments(by_line[0x7FE][0]),
                [newest_index, newest_timestamp],
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "83746bfa55e43ee7e2dab8fd079d7e7d"
            "96b2c4a51b0aaf24c490eb0256e5050a",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "0e7d10191ac39529a7fa12b1d70400474"
            "bf0990f47fc27b93177158dc6c072df",
        )


if __name__ == "__main__":
    unittest.main()
