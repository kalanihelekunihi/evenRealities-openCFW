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
SOURCE = COMPONENT_ROOT / "mram_find_by_ltk_request.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_find_by_ltk_request_host.c"
)
RECORD_COUNT = 10
RECORD_SIZE = 200


class MramFindByLtkRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_find_by_ltk_request.dylib"
            if sys.platform == "darwin"
            else "mram_find_by_ltk_request.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_ltk_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.find = cls.loaded.open_cfw_mram_find_by_ltk_request
        cls.find.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.find.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.records = (
            ctypes.c_ubyte * (RECORD_COUNT * RECORD_SIZE)
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_ltk_records",
        )
        self.compare_indices = (
            ctypes.c_uint * RECORD_COUNT
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_ltk_compare_indices",
        )
        self.compare_lengths = (
            ctypes.c_uint * RECORD_COUNT
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_ltk_compare_lengths",
        )
        self.base = ctypes.addressof(self.records)

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, index: int) -> int:
        return self.base + index * RECORD_SIZE

    def set_byte(self, index: int, offset: int, value: int) -> None:
        self.records[index * RECORD_SIZE + offset] = value

    def set_random(self, index: int, random_number: bytes) -> None:
        self.assertEqual(len(random_number), 8)
        for offset, value in enumerate(random_number):
            self.set_byte(index, 0x44 + offset, value)

    def set_diversifier(self, index: int, value: int) -> None:
        ctypes.c_ushort.from_buffer(
            self.records,
            index * RECORD_SIZE + 0x4C,
        ).value = value

    def set_timestamp(self, index: int, value: int) -> None:
        ctypes.c_uint.from_buffer(
            self.records,
            index * RECORD_SIZE + 0xC4,
        ).value = value

    def timestamp(self, index: int) -> int:
        return ctypes.c_uint.from_buffer(
            self.records,
            index * RECORD_SIZE + 0xC4,
        ).value

    def random_buffer(
        self,
        random_number: bytes,
    ) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * 8)(*random_number)

    def test_filters_before_compare_and_refreshes_first_match(
        self,
    ) -> None:
        wanted = bytes.fromhex("0011223344556677")
        other = bytes.fromhex("0011223344556678")
        self.word("open_cfw_test_mram_ltk_counter").value = 900

        self.set_byte(0, 0x2F, 0)
        self.set_diversifier(0, 0x1234)
        self.set_random(0, wanted)
        self.set_byte(1, 0x2F, 1)
        self.set_diversifier(1, 0x1235)
        self.set_random(1, wanted)
        self.set_byte(3, 0x2F, 2)
        self.set_diversifier(3, 0x1234)
        self.set_random(3, other)
        self.set_timestamp(3, 333)
        self.set_byte(6, 0x2F, 0xFF)
        self.set_diversifier(6, 0x1234)
        self.set_random(6, wanted)

        result = self.find(
            0xABCD1234,
            self.random_buffer(wanted),
        )

        self.assertEqual(result, self.pointer(6))
        self.assertEqual(list(self.compare_indices)[:2], [3, 6])
        self.assertEqual(list(self.compare_lengths)[:2], [8, 8])
        self.assertEqual(
            self.word("open_cfw_test_mram_ltk_compare_calls").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_ltk_counter").value,
            901,
        )
        self.assertEqual(self.timestamp(3), 333)
        self.assertEqual(self.timestamp(6), 901)

    def test_first_match_wins_and_counter_wraps(self) -> None:
        wanted = bytes.fromhex("8899aabbccddeeff")
        for index in (2, 7):
            self.set_byte(index, 0x2F, 1)
            self.set_diversifier(index, 0xBEEF)
            self.set_random(index, wanted)
            self.set_timestamp(index, 100 + index)
        self.word("open_cfw_test_mram_ltk_counter").value = 0xFFFFFFFF

        result = self.find(0xBEEF, self.random_buffer(wanted))

        self.assertEqual(result, self.pointer(2))
        self.assertEqual(list(self.compare_indices)[:1], [2])
        self.assertEqual(
            self.word("open_cfw_test_mram_ltk_counter").value,
            0,
        )
        self.assertEqual(self.timestamp(2), 0)
        self.assertEqual(self.timestamp(7), 107)

    def test_no_match_scans_all_eligible_records(self) -> None:
        wanted = bytes.fromhex("1020304050607080")
        for index in range(RECORD_COUNT):
            self.set_byte(index, 0x2F, index + 1)
            self.set_diversifier(index, 0xCAFE)
            self.set_random(
                index,
                bytes([1, 2, 3, 4, 5, 6, 7, index]),
            )
            self.set_timestamp(index, 0x1000 + index)
        self.word("open_cfw_test_mram_ltk_counter").value = 7

        result = self.find(0xCAFE, self.random_buffer(wanted))

        self.assertIsNone(result)
        self.assertEqual(
            list(self.compare_indices),
            list(range(RECORD_COUNT)),
        )
        self.assertEqual(
            list(self.compare_lengths),
            [8] * RECORD_COUNT,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_ltk_counter").value,
            7,
        )
        self.assertEqual(
            [self.timestamp(index) for index in range(RECORD_COUNT)],
            [0x1000 + index for index in range(RECORD_COUNT)],
        )

    def test_null_random_is_not_rejected_before_candidate_compare(
        self,
    ) -> None:
        self.set_byte(9, 0x2F, 1)
        self.set_diversifier(9, 0x9876)

        result = self.find(0x9876, None)

        self.assertIsNone(result)
        self.assertEqual(
            self.word("open_cfw_test_mram_ltk_compare_calls").value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_ltk_null_compare_calls"
            ).value,
            1,
        )
        self.assertEqual(self.compare_indices[0], 9)
        self.assertEqual(self.compare_lengths[0], 8)

    def test_randomized_model_matches_first_eligible_record(self) -> None:
        generator = random.Random(0x47ADD4)

        for _ in range(200):
            self.reset()
            diversifier = generator.randrange(0x10000)
            wanted = bytes(generator.randrange(256) for _ in range(8))
            initial_counter = generator.randrange(0x100000000)
            expected = None
            self.word(
                "open_cfw_test_mram_ltk_counter"
            ).value = initial_counter

            for index in range(RECORD_COUNT):
                active = generator.randrange(4)
                record_diversifier = generator.randrange(0x10000)
                random_number = bytes(
                    generator.randrange(256) for _ in range(8)
                )
                if generator.randrange(5) == 0:
                    record_diversifier = diversifier
                    random_number = wanted
                self.set_byte(index, 0x2F, active)
                self.set_diversifier(index, record_diversifier)
                self.set_random(index, random_number)
                self.set_timestamp(index, 0x40000000 + index)
                if (
                    expected is None
                    and active != 0
                    and record_diversifier == diversifier
                    and random_number == wanted
                ):
                    expected = index

            result = self.find(
                diversifier | 0xABCD0000,
                self.random_buffer(wanted),
            )

            if expected is None:
                self.assertIsNone(result)
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_ltk_counter"
                    ).value,
                    initial_counter,
                )
            else:
                updated = (initial_counter + 1) & 0xFFFFFFFF
                self.assertEqual(result, self.pointer(expected))
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_ltk_counter"
                    ).value,
                    updated,
                )
                self.assertEqual(self.timestamp(expected), updated)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "bfd7de15454c63daecd39cdbea4fa10503d5b2565c451ba601a4f13736bea856",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "7889a9478969f9428f91b8a8a2d34663b4c149c49a093317740c727c43bc9d53",
        )


if __name__ == "__main__":
    unittest.main()
