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
SOURCE = COMPONENT_ROOT / "mram_reset_record_timestamps.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_reset_record_timestamps_host.c"
)
CAPTURE_COUNT = 128
CAPTURE_WIDTH = 9
RECORD_COUNT = 10
RECORD_SIZE = 200


class MramResetRecordTimestampsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_reset_record_timestamps.dylib"
            if sys.platform == "darwin"
            else "mram_reset_record_timestamps.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_renumber_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.renumber = cls.loaded.open_cfw_mram_reset_record_timestamps
        cls.renumber.argtypes = []
        cls.renumber.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def words(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_uint * count).in_dll(self.loaded, name)

    def addresses(self, name: str, count: int) -> ctypes.Array:
        return (ctypes.c_size_t * count).in_dll(self.loaded, name)

    def records(self) -> ctypes.Array:
        return (ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)).in_dll(
            self.loaded,
            "open_cfw_test_mram_renumber_records",
        )

    def timestamp(self, index: int) -> int:
        start = index * RECORD_SIZE + 0xC4
        return int.from_bytes(bytes(self.records()[start:start + 4]), "little")

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_renumber_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_renumber_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def log_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_renumber_log_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_renumber_logs",
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
            "open_cfw_test_mram_renumber_trace_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_renumber_traces",
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

    def activate(self, index: int, allocated: int = 1, active: int = 1) -> None:
        records = self.records()
        records[index * RECORD_SIZE + 0x2F] = allocated
        records[index * RECORD_SIZE + 0x30] = active

    def test_renumbers_only_allocated_active_records_in_slot_order(self) -> None:
        records = self.records()
        self.word("open_cfw_test_mram_renumber_counter").value = 0xFFFFFFFF
        for index in range(RECORD_COUNT):
            records[index * RECORD_SIZE + 0xC4:index * RECORD_SIZE + 0xC8] = (
                (0xA0000000 + index).to_bytes(4, "little")
            )
        self.activate(1)
        self.activate(3, allocated=2, active=7)
        self.activate(4, allocated=0, active=1)
        self.activate(8, allocated=1, active=0)
        self.activate(9)

        self.renumber()

        self.assertEqual(
            self.word("open_cfw_test_mram_renumber_counter").value,
            3,
        )
        self.assertEqual(
            [self.timestamp(index) for index in range(RECORD_COUNT)],
            [
                0xA0000000,
                1,
                0xA0000002,
                2,
                0xA0000004,
                0xA0000005,
                0xA0000006,
                0xA0000007,
                0xA0000008,
                3,
            ],
        )

    def test_persists_each_selected_record_and_ignores_results(self) -> None:
        for index in (0, 2, 7):
            self.activate(index)
        self.word("open_cfw_test_mram_renumber_update_result").value = (
            0xFFFFFFFF
        )

        self.renumber()

        self.assertEqual(
            self.word("open_cfw_test_mram_renumber_update_count").value,
            3,
        )
        records = self.records()
        base = ctypes.addressof(records)
        self.assertEqual(
            list(
                self.addresses(
                    "open_cfw_test_mram_renumber_updates",
                    CAPTURE_COUNT,
                )[:3]
            ),
            [base, base + 2 * RECORD_SIZE, base + 7 * RECORD_SIZE],
        )

    def test_all_enabled_diagnostics_match_stock_metadata(self) -> None:
        self.activate(4)
        self.word(
            "open_cfw_test_mram_renumber_level_default"
        ).value = 7

        self.renumber()

        self.assertEqual(
            self.log_records(),
            [
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x00775194,
                    0x82B,
                    0x0071285C,
                    0,
                    0,
                    0,
                ],
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x00775194,
                    0x835,
                    0x00712898,
                    2,
                    4,
                    1,
                ],
                [
                    4,
                    0x0078A0D0,
                    0x006D84BC,
                    0x00775194,
                    0x83E,
                    0x007128D4,
                    0,
                    0,
                    0,
                ],
            ],
        )
        self.assertEqual(
            self.trace_records(),
            [
                [0x10000000, 0x00700524, 0x00700524, 0, 0, 0, 0, 0, 0],
                [0x10800000, 0x006F863C, 0x006F863C, 2, 4, 1, 0, 0, 0],
                [0x10000000, 0x006F8684, 0x006F8684, 0, 0, 0, 0, 0, 0],
            ],
        )
        self.assertEqual(
            self.order(),
            [1, 2, 1, 3, 1, 2, 1, 3, 4, 1, 2, 1, 3],
        )

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        self.word(
            "open_cfw_test_mram_renumber_level_default"
        ).value = 2
        self.renumber()
        self.assertEqual(
            [record[4] for record in self.log_records()],
            [0x82B, 0x83E],
        )
        self.assertEqual(self.trace_records(), [])
        self.assertEqual(self.order(), [1, 2, 1, 1, 1, 2, 1, 1])

        self.reset()
        self.word(
            "open_cfw_test_mram_renumber_level_default"
        ).value = 4
        self.renumber()
        self.assertEqual(self.log_records(), [])
        self.assertEqual(
            [record[0] for record in self.trace_records()],
            [0x10000000, 0x10000000],
        )
        self.assertEqual(self.order(), [1, 1, 1, 3, 1, 1, 1, 3])

        self.reset()
        self.word(
            "open_cfw_test_mram_renumber_level_default"
        ).value = 1
        self.renumber()
        self.assertEqual(self.log_records(), [])
        self.assertEqual(
            [record[0] for record in self.trace_records()],
            [0x10000000, 0x10000000],
        )
        self.assertEqual(self.order(), [1, 1, 3, 1, 1, 3])

    def test_randomized_model_preserves_unselected_records(self) -> None:
        generator = random.Random(0x47C164)
        for _ in range(500):
            self.reset()
            records = self.records()
            initial = bytearray(generator.randbytes(len(records)))
            records[:] = initial
            selected = []
            for index in range(RECORD_COUNT):
                allocated = generator.randrange(4)
                active = generator.randrange(4)
                records[index * RECORD_SIZE + 0x2F] = allocated
                records[index * RECORD_SIZE + 0x30] = active
                initial[index * RECORD_SIZE + 0x2F] = allocated
                initial[index * RECORD_SIZE + 0x30] = active
                if allocated != 0 and active != 0:
                    selected.append(index)

            self.renumber()

            expected = bytearray(initial)
            for timestamp, index in enumerate(selected, 1):
                start = index * RECORD_SIZE + 0xC4
                expected[start:start + 4] = timestamp.to_bytes(4, "little")
            self.assertEqual(bytes(records), bytes(expected))
            self.assertEqual(
                self.word("open_cfw_test_mram_renumber_counter").value,
                len(selected),
            )
            self.assertEqual(
                self.word(
                    "open_cfw_test_mram_renumber_update_count"
                ).value,
                len(selected),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "80e453a638f4e0965cfe0e9f8b7587b241746e4fc27d882200a57cdf3944a82c",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "a7cffc2768543ac389773b8284c7ec3a162bdbe0fda84aef4a50c3e0f83ee01d",
        )


if __name__ == "__main__":
    unittest.main()
