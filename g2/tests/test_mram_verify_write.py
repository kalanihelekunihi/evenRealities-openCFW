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
SOURCE = COMPONENT_ROOT / "mram_verify_write.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_verify_write_host.c"
)
CAPTURE_COUNT = 256
NVM_SIZE = 10 * 0x100


class MramVerifyWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_verify_write.dylib"
            if sys.platform == "darwin"
            else "mram_verify_write.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_verify_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.verify = cls.loaded.open_cfw_mram_verify_write
        cls.verify.argtypes = [ctypes.c_void_p]
        cls.verify.restype = ctypes.c_uint

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
        return (ctypes.c_ubyte * NVM_SIZE).in_dll(
            self.loaded,
            "open_cfw_test_mram_verify_nvm",
        )

    def order(self) -> list[int]:
        count = self.word(
            "open_cfw_test_mram_verify_order_count"
        ).value
        return list(
            self.words(
                "open_cfw_test_mram_verify_order",
                CAPTURE_COUNT,
            )[:count]
        )

    def set_slot(self, index: int, record: ctypes.Array) -> None:
        destination = self.nvm()
        start = index * 0x100
        destination[start:start + 200] = bytes(record)

    def record(self, seed: int = 0x20) -> ctypes.Array:
        value = (ctypes.c_ubyte * 200)()
        for index in range(200):
            value[index] = (seed + index * 17) & 0xFF
        return value

    def configure_full_logging(self) -> None:
        self.word(
            "open_cfw_test_mram_verify_level_default"
        ).value = 7

    def log_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_verify_log_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_verify_logs",
            CAPTURE_COUNT * 9,
        )
        return [
            list(values[index * 9:(index + 1) * 9])
            for index in range(count)
        ]

    def trace_records(self) -> list[list[int]]:
        count = self.word(
            "open_cfw_test_mram_verify_trace_count"
        ).value
        values = self.addresses(
            "open_cfw_test_mram_verify_traces",
            CAPTURE_COUNT * 6,
        )
        return [
            list(values[index * 6:(index + 1) * 6])
            for index in range(count)
        ]

    def test_no_match_is_success_after_scanning_all_slots(self) -> None:
        self.configure_full_logging()
        record = self.record()
        record[6] = 2
        for index in range(10):
            slot = self.record(0x80 + index)
            slot[6] = 2
            self.set_slot(index, slot)

        result = self.verify(record)

        self.assertEqual(result, 1)
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_verify_cache_count"
            ).value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_mram_verify_cache_range"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_verify_cache_clean"
            ).value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_verify_compare_count"
            ).value,
            10,
        )
        self.assertEqual(
            [record[4] for record in self.log_records()],
            [0x779, 0x7C2],
        )
        self.assertEqual(self.order()[4], 4)

    def test_identifier_and_owner_select_first_matching_slot(self) -> None:
        self.configure_full_logging()
        record = self.record()
        record[6] = 3
        record[0x2E] = 0
        wrong_owner = self.record()
        wrong_owner[6] = 4
        wrong_owner[0x2E] = 0
        match = self.record()
        match[6] = 3
        match[0x2E] = 0
        self.set_slot(2, wrong_owner)
        self.set_slot(4, match)

        result = self.verify(record)

        self.assertEqual(result, 1)
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_verify_compare_count"
            ).value,
            5,
        )
        found = next(
            item
            for item in self.log_records()
            if item[4] == 0x782
        )
        self.assertEqual(
            found,
            [
                4, 0x0078A0D0, 0x006D84BC, 0x00775164,
                0x782, 0x0071C150, 1, 4, 0,
            ],
        )

    def test_all_selected_key_classes_verify_and_peer_ltk_is_ignored(
        self,
    ) -> None:
        self.configure_full_logging()
        record = self.record()
        record[6] = 1
        record[0x2E] = 0x0F
        match = self.record()
        match[6] = 1
        match[0x2E] = 0x0F
        for index in range(0x50, 0x6A):
            match[index] ^= 0xFF
        self.set_slot(0, match)

        result = self.verify(record)

        self.assertEqual(result, 1)
        compares = self.addresses(
            "open_cfw_test_mram_verify_compares",
            CAPTURE_COUNT * 3,
        )
        self.assertEqual(
            [compares[index * 3 + 2] for index in range(4)],
            [6, 16, 16, 16],
        )
        self.assertEqual(
            [item[4] for item in self.log_records()],
            [0x779, 0x782, 0x79F, 0x7AB, 0x7B7, 0x7C2],
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_verify_hex_count"
            ).value,
            0,
        )

    def test_field_mismatches_report_ram_then_flash_values(self) -> None:
        self.configure_full_logging()
        record = self.record()
        record[6] = 1
        record[0x30] = 7
        record[0x2F] = 8
        record[0x2E] = 0
        match = self.record()
        match[6] = 1
        match[0x30] = 17
        match[0x2F] = 18
        match[0x2E] = 2
        self.set_slot(0, match)

        result = self.verify(record)

        self.assertEqual(result, 0)
        failures = [
            item
            for item in self.log_records()
            if item[4] in (0x787, 0x78D, 0x793)
        ]
        self.assertEqual(
            [(item[4], item[7], item[8]) for item in failures],
            [
                (0x787, 7, 17),
                (0x78D, 8, 18),
                (0x793, 0, 2),
            ],
        )
        final = self.log_records()[-1]
        self.assertEqual(
            final[:7],
            [
                1, 0x0078A0D0, 0x006D84BC, 0x00775164,
                0x7C4, 0x006E63D0, 0,
            ],
        )

    def test_every_selected_key_mismatch_dumps_ram_then_flash(
        self,
    ) -> None:
        self.configure_full_logging()
        record = self.record()
        record[6] = 1
        record[0x2E] = 0x0D
        match = self.record()
        match[6] = 1
        match[0x2E] = 0x0D
        for offset in (0x34, 0x07, 0x1E):
            match[offset] ^= 0xFF
        self.set_slot(0, match)

        result = self.verify(record)

        self.assertEqual(result, 0)
        self.assertEqual(
            [item[4] for item in self.log_records()],
            [0x779, 0x782, 0x79A, 0x7A6, 0x7B2, 0x7C4],
        )
        hexes = self.addresses(
            "open_cfw_test_mram_verify_hexes",
            CAPTURE_COUNT * 4,
        )
        self.assertEqual(
            [hexes[index * 4] for index in range(6)],
            [
                0x0078CA5C, 0x0078A118,
                0x0078CA64, 0x0078A124,
                0x0078A130, 0x0078A13C,
            ],
        )
        self.assertEqual(
            [
                (hexes[index * 4 + 1], hexes[index * 4 + 3])
                for index in range(6)
            ],
            [(16, 16)] * 6,
        )

    def test_structured_and_trace_gates_remain_independent(self) -> None:
        record = self.record()
        for level, logs, traces, prefix in (
            (2, 2, 0, [1, 2, 1, 1, 4]),
            (1, 0, 2, [1, 1, 3, 4]),
            (4, 0, 2, [1, 1, 1, 3, 4]),
        ):
            with self.subTest(level=level):
                self.reset()
                self.word(
                    "open_cfw_test_mram_verify_level_default"
                ).value = level

                self.verify(record)

                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_verify_log_count"
                    ).value,
                    logs,
                )
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_verify_trace_count"
                    ).value,
                    traces,
                )
                self.assertEqual(self.order()[:len(prefix)], prefix)

    def test_randomized_model_matches_first_persisted_record(
        self,
    ) -> None:
        generator = random.Random(0x47B730)
        for iteration in range(500):
            with self.subTest(iteration=iteration):
                self.reset()
                record = self.record(generator.randrange(256))
                record[6] = generator.randrange(4)
                record[0x2E] = generator.randrange(16)
                slots: list[bytearray] = []
                for index in range(10):
                    slot = bytearray(
                        generator.randrange(256) for _ in range(200)
                    )
                    slots.append(slot)
                    self.nvm()[
                        index * 0x100:index * 0x100 + 200
                    ] = slot
                matching = [
                    index
                    for index, slot in enumerate(slots)
                    if slot[:6] == bytes(record[:6])
                    and slot[6] == record[6]
                ]
                if generator.randrange(2) != 0:
                    target = generator.randrange(10)
                    slot = bytearray(record)
                    for index in range(200):
                        if generator.randrange(5) == 0:
                            slot[index] = generator.randrange(256)
                    slot[:7] = bytes(record[:7])
                    slots[target] = slot
                    self.nvm()[
                        target * 0x100:target * 0x100 + 200
                    ] = slot
                    matching = [
                        index
                        for index, value in enumerate(slots)
                        if value[:6] == bytes(record[:6])
                        and value[6] == record[6]
                    ]

                expected = 1
                if matching:
                    slot = slots[matching[0]]
                    if (
                        slot[0x30] != record[0x30]
                        or slot[0x2F] != record[0x2F]
                        or slot[0x2E] != record[0x2E]
                    ):
                        expected = 0
                    for mask, offset in (
                        (1, 0x34),
                        (4, 0x07),
                        (8, 0x1E),
                    ):
                        if (
                            record[0x2E] & mask
                            and slot[offset:offset + 16]
                            != bytes(record[offset:offset + 16])
                        ):
                            expected = 0

                self.assertEqual(self.verify(record), expected)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "58173eeb43aa84f29b4a6b2e452c5808e3e23b5c076819fbfa56d7f344663699",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "6c142c280bb090ec8880cbe3420c6065bd78279570ba1ab7eabeb8f250b1a827",
        )


if __name__ == "__main__":
    unittest.main()
