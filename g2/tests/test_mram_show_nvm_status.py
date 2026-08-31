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
SOURCE = COMPONENT_ROOT / "mram_show_nvm_status.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "mram_show_nvm_status_host.c"
CAPTURE_COUNT = 128
CAPTURE_WIDTH = 16
RECORD_COUNT = 10
RECORD_SIZE = 256


class MramShowNvmStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_show_nvm_status.dylib"
            if sys.platform == "darwin"
            else "mram_show_nvm_status.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_nvm_status_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.show = cls.loaded.open_cfw_mram_show_nvm_status
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

    def records(self) -> ctypes.Array:
        return (ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)).in_dll(
            self.loaded,
            "open_cfw_test_mram_nvm_status_records",
        )

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_nvm_status_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_nvm_status_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def captures(self, name: str, count_name: str) -> list[list[int]]:
        count = self.word(count_name).value
        values = self.addresses(name, CAPTURE_COUNT * CAPTURE_WIDTH)
        return [
            list(
                values[
                    index * CAPTURE_WIDTH:
                    (index + 1) * CAPTURE_WIDTH
                ]
            )
            for index in range(count)
        ]

    def logs(self) -> list[list[int]]:
        return self.captures(
            "open_cfw_test_mram_nvm_status_logs",
            "open_cfw_test_mram_nvm_status_log_count",
        )

    def traces(self) -> list[list[int]]:
        return self.captures(
            "open_cfw_test_mram_nvm_status_traces",
            "open_cfw_test_mram_nvm_status_trace_count",
        )

    def configure(
        self,
        index: int,
        identifier: bytes,
        *,
        in_use: int = 1,
        valid: int = 1,
        key_mask: int = 0xA5,
    ) -> None:
        records = self.records()
        start = index * RECORD_SIZE
        records[start:start + 6] = identifier
        records[start + 0x2E] = key_mask
        records[start + 0x2F] = in_use
        records[start + 0x30] = valid

    def test_selection_and_summary_follow_exact_nvm_rules(self) -> None:
        self.configure(0, b"\x00\x00\x00\x00\x10\x11")
        self.configure(1, b"\xff\xff\xff\xff\x10\x11")
        self.configure(2, b"\x01\x00\x00\x00\x10\x11", in_use=0)
        self.configure(3, b"\x02\x00\x00\x00\x10\x11", valid=0)
        self.configure(4, b"\x03\x00\x00\x00\x10\x11")
        self.configure(9, b"\x04\x00\x00\x00\x20\x21")
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 2

        before = bytes(self.records())
        self.show()

        self.assertEqual(bytes(self.records()), before)
        self.assertEqual(
            [record[7] for record in self.logs() if record[4] == 0x85B],
            [4, 9],
        )
        summary = next(record for record in self.logs() if record[4] == 0x860)
        self.assertEqual(summary[7:9], [2, 10])

    def test_record_diagnostic_preserves_index_mask_and_byte_order(self) -> None:
        self.configure(
            7,
            b"\x10\x20\x30\x40\x50\x60",
            key_mask=0xD3,
        )
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 7

        self.show()

        structured = next(
            record for record in self.logs() if record[4] == 0x85B
        )
        self.assertEqual(
            structured[:15],
            [
                4,
                0x0078A0D0,
                0x006D84BC,
                0x0077DE0C,
                0x85B,
                0x006EB6C8,
                8,
                7,
                0xD3,
                0x60,
                0x50,
                0x40,
                0x30,
                0x20,
                0x10,
            ],
        )
        trace = next(
            record for record in self.traces() if record[0] == 0x12000000
        )
        self.assertEqual(
            trace[:12],
            [
                0x12000000,
                0x006E2598,
                0x006E2598,
                8,
                7,
                0xD3,
                0x60,
                0x50,
                0x40,
                0x30,
                0x20,
                0x10,
            ],
        )

    def test_boundary_and_geometry_diagnostics_match_stock_metadata(self) -> None:
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 7

        self.show()

        self.assertEqual(
            [(record[4], record[5]) for record in self.logs()],
            [
                (0x84B, 0x00769468),
                (0x860, 0x0075DED0),
                (0x861, 0x0077DE20),
                (0x862, 0x00751F80),
                (0x863, 0x0075DF10),
            ],
        )
        self.assertEqual(self.logs()[1][7:9], [0, 10])
        self.assertEqual(self.logs()[2][7], 0x007FF000)
        self.assertEqual(self.logs()[3][7:9], [0x100, 0x40])
        self.assertEqual(
            [(record[0], record[1], record[4:6]) for record in self.traces()],
            [
                (0x10000000, 0x00747954, [0, 0]),
                (0x10800000, 0x0073C16C, [0, 10]),
                (0x10400000, 0x0075DEF0, [0x007FF000, 0]),
                (0x10800000, 0x0073C198, [0x100, 0x40]),
                (0x10000000, 0x0073C1C4, [0, 0]),
            ],
        )

    def test_clean_cache_invalidation_precedes_scan_and_result_is_ignored(
        self,
    ) -> None:
        self.configure(0, b"\x01\x02\x03\x04\x05\x06")
        self.word(
            "open_cfw_test_mram_nvm_status_cache_result"
        ).value = 0xFFFFFFFF
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 0

        self.show()

        self.assertEqual(
            self.word("open_cfw_test_mram_nvm_status_cache_count").value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_nvm_status_cache_range"
            ).value,
            0,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_nvm_status_cache_clean").value,
            1,
        )
        self.assertEqual(self.order(), [1, 1, 1, 4] + [1, 1, 1] * 5)

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 2
        self.show()
        self.assertEqual(len(self.logs()), 5)
        self.assertEqual(self.traces(), [])

        self.reset()
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 4
        self.show()
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 5)

        self.reset()
        self.word(
            "open_cfw_test_mram_nvm_status_level_default"
        ).value = 1
        self.show()
        self.assertEqual(self.logs(), [])
        self.assertEqual(len(self.traces()), 5)

    def test_randomized_model_matches_valid_record_filter(self) -> None:
        generator = random.Random(0x47C2BC)
        for _ in range(500):
            self.reset()
            records = self.records()
            records[:] = generator.randbytes(len(records))
            selected = []
            for index in range(RECORD_COUNT):
                start = index * RECORD_SIZE
                identifier = generator.getrandbits(32)
                records[start:start + 4] = identifier.to_bytes(4, "little")
                records[start + 0x2F] = generator.randrange(4)
                records[start + 0x30] = generator.randrange(4)
                if (
                    records[start + 0x2F] != 0
                    and records[start + 0x30] != 0
                    and identifier not in (0, 0xFFFFFFFF)
                ):
                    selected.append(index)
            self.word(
                "open_cfw_test_mram_nvm_status_level_default"
            ).value = 2

            before = bytes(records)
            self.show()

            self.assertEqual(bytes(records), before)
            self.assertEqual(
                [
                    record[7]
                    for record in self.logs()
                    if record[4] == 0x85B
                ],
                selected,
            )
            summary = next(
                record for record in self.logs() if record[4] == 0x860
            )
            self.assertEqual(summary[7:9], [len(selected), 10])

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0b4671ded7d8d28207666abea057bf09f1ba5ae8fd9405c1b1a84002659c3bd6",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "741d482a781216dc49fe93b4ab97fef96aca71f46c735b63569169d740acf87c",
        )


if __name__ == "__main__":
    unittest.main()
