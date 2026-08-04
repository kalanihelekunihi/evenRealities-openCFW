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
SOURCE = COMPONENT_ROOT / "mram_find_by_address.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_find_by_address_host.c"
)
RECORD_COUNT = 10
RECORD_SIZE = 200


class MramFindByAddressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_find_by_address.dylib"
            if sys.platform == "darwin"
            else "mram_find_by_address.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_find_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.find = cls.loaded.open_cfw_mram_find_by_address
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
            "open_cfw_test_mram_find_records",
        )
        self.compare_indices = (
            ctypes.c_uint * RECORD_COUNT
        ).in_dll(
            self.loaded,
            "open_cfw_test_mram_find_compare_indices",
        )
        self.base = ctypes.addressof(self.records)

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def pointer(self, index: int) -> int:
        return self.base + index * RECORD_SIZE

    def set_byte(self, index: int, offset: int, value: int) -> None:
        self.records[index * RECORD_SIZE + offset] = value

    def set_address(self, index: int, address: bytes) -> None:
        self.assertEqual(len(address), 6)
        for offset, value in enumerate(address):
            self.set_byte(index, offset, value)

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

    def address_buffer(self, address: bytes) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * 6)(*address)

    def test_owner_mapping_short_circuit_and_timestamp_refresh(
        self,
    ) -> None:
        wanted = bytes.fromhex("102030405060")
        other = bytes.fromhex("102030405061")
        self.word(
            "open_cfw_test_mram_find_mapping_enabled"
        ).value = 1
        self.word("open_cfw_test_mram_find_counter").value = 41

        self.set_byte(0, 0x2F, 0)
        self.set_byte(0, 6, 0)
        self.set_address(0, wanted)
        self.set_byte(1, 0x2F, 1)
        self.set_byte(1, 6, 1)
        self.set_address(1, wanted)
        self.set_byte(2, 0x2F, 1)
        self.set_byte(2, 6, 0)
        self.set_address(2, other)
        self.set_timestamp(2, 0x22222222)
        self.set_byte(4, 0x2F, 0xFF)
        self.set_byte(4, 6, 0)
        self.set_address(4, wanted)

        result = self.find(0xABCD0102, self.address_buffer(wanted))

        self.assertEqual(result, self.pointer(4))
        self.assertEqual(
            self.word("open_cfw_test_mram_find_map_calls").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_map_input").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_map_output").value,
            0,
        )
        self.assertEqual(
            list(self.compare_indices)[:2],
            [2, 4],
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_compare_calls").value,
            2,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_counter").value,
            42,
        )
        self.assertEqual(self.timestamp(2), 0x22222222)
        self.assertEqual(self.timestamp(4), 42)

    def test_first_match_wins_and_counter_wraps(self) -> None:
        wanted = bytes.fromhex("a1a2a3a4a5a6")
        for index in (1, 8):
            self.set_byte(index, 0x2F, 1)
            self.set_byte(index, 6, 3)
            self.set_address(index, wanted)
            self.set_timestamp(index, 0x11111111 + index)
        self.word("open_cfw_test_mram_find_counter").value = 0xFFFFFFFF

        result = self.find(3, self.address_buffer(wanted))

        self.assertEqual(result, self.pointer(1))
        self.assertEqual(
            list(self.compare_indices)[:1],
            [1],
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_counter").value,
            0,
        )
        self.assertEqual(self.timestamp(1), 0)
        self.assertEqual(self.timestamp(8), 0x11111119)

    def test_no_match_scans_all_candidates_without_refresh(self) -> None:
        wanted = bytes.fromhex("010203040506")
        for index in range(RECORD_COUNT):
            self.set_byte(index, 0x2F, index + 1)
            self.set_byte(index, 6, 7)
            self.set_address(
                index,
                bytes([1, 2, 3, 4, 5, index + 10]),
            )
            self.set_timestamp(index, 1000 + index)
        self.word("open_cfw_test_mram_find_counter").value = 77

        result = self.find(0x107, self.address_buffer(wanted))

        self.assertIsNone(result)
        self.assertEqual(
            list(self.compare_indices),
            list(range(RECORD_COUNT)),
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_compare_calls").value,
            RECORD_COUNT,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_counter").value,
            77,
        )
        self.assertEqual(
            [self.timestamp(index) for index in range(RECORD_COUNT)],
            [1000 + index for index in range(RECORD_COUNT)],
        )

    def test_null_address_is_not_rejected_before_candidate_compare(
        self,
    ) -> None:
        self.set_byte(9, 0x2F, 1)
        self.set_byte(9, 6, 5)

        result = self.find(5, None)

        self.assertIsNone(result)
        self.assertEqual(
            self.word("open_cfw_test_mram_find_map_calls").value,
            1,
        )
        self.assertEqual(
            self.word("open_cfw_test_mram_find_compare_calls").value,
            1,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_find_null_compare_calls"
            ).value,
            1,
        )
        self.assertEqual(self.compare_indices[0], 9)

    def test_randomized_model_matches_first_eligible_record(self) -> None:
        generator = random.Random(0x47AD74)

        for _ in range(200):
            self.reset()
            mapping_enabled = generator.randrange(2)
            owner = generator.randrange(256)
            mapped = owner
            if mapping_enabled and mapped == 2:
                mapped = 0
            elif mapping_enabled and mapped == 3:
                mapped = 1
            wanted = bytes(generator.randrange(256) for _ in range(6))
            expected = None
            initial_counter = generator.randrange(0x100000000)
            self.word(
                "open_cfw_test_mram_find_mapping_enabled"
            ).value = mapping_enabled
            self.word(
                "open_cfw_test_mram_find_counter"
            ).value = initial_counter

            for index in range(RECORD_COUNT):
                active = generator.randrange(4)
                record_owner = generator.randrange(8)
                address = bytes(
                    generator.randrange(256) for _ in range(6)
                )
                if generator.randrange(5) == 0:
                    record_owner = mapped
                    address = wanted
                self.set_byte(index, 0x2F, active)
                self.set_byte(index, 6, record_owner)
                self.set_address(index, address)
                self.set_timestamp(index, 0x80000000 + index)
                if (
                    expected is None
                    and active != 0
                    and record_owner == mapped
                    and address == wanted
                ):
                    expected = index

            result = self.find(owner, self.address_buffer(wanted))

            if expected is None:
                self.assertIsNone(result)
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_find_counter"
                    ).value,
                    initial_counter,
                )
            else:
                updated = (initial_counter + 1) & 0xFFFFFFFF
                self.assertEqual(result, self.pointer(expected))
                self.assertEqual(
                    self.word(
                        "open_cfw_test_mram_find_counter"
                    ).value,
                    updated,
                )
                self.assertEqual(self.timestamp(expected), updated)

    def test_sources_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "0933cf28a25807208894697dd0ba04aeff634de6cb08d2d6f16ceb61502c58a9",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9a42cf11d9e47f5f483702d48641a1088160b6f02e74d0a3c2b609704d16ec8e",
        )


if __name__ == "__main__":
    unittest.main()
