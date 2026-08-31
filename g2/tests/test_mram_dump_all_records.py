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
SOURCE = COMPONENT_ROOT / "mram_dump_all_records.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_dump_all_records_host.c"
)


class MramDumpAllRecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_dump_all_records.dylib"
            if sys.platform == "darwin"
            else "mram_dump_all_records.so"
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
        cls.reset = cls.loaded.open_cfw_test_mram_dump_all_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.dump = cls.loaded.open_cfw_mram_dump_all_records
        cls.dump.argtypes = []
        cls.dump.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def records(self) -> ctypes.Array:
        return (ctypes.c_ubyte * 2000).in_dll(
            self.loaded,
            "open_cfw_test_mram_dump_all_records",
        )

    def test_walks_exactly_ten_records_in_slot_order(self) -> None:
        records = self.records()

        self.dump()

        pointers = (ctypes.c_size_t * 10).in_dll(
            self.loaded,
            "open_cfw_test_mram_dump_all_record_pointers",
        )
        indices = (ctypes.c_uint * 10).in_dll(
            self.loaded,
            "open_cfw_test_mram_dump_all_indices",
        )
        self.assertEqual(
            list(pointers),
            [
                ctypes.addressof(records) + 200 * index
                for index in range(10)
            ],
        )
        self.assertEqual(list(indices), list(range(10)))
        self.assertEqual(
            self.word("open_cfw_test_mram_dump_all_dump_count").value,
            10,
        )

    def test_record_table_holder_is_sampled_once(self) -> None:
        self.dump()

        self.assertEqual(
            self.word("open_cfw_test_mram_dump_all_base_count").value,
            1,
        )

    def test_iteration_does_not_mutate_record_bytes(self) -> None:
        generator = random.Random(0x47CA9C)
        records = self.records()
        records[:] = generator.randbytes(len(records))
        before = bytes(records)

        self.dump()

        self.assertEqual(bytes(records), before)

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c9d3b003356269f75a07b805cb3c02f759f77df835563b57b8ffc533b84de402",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "06a5f200258efb4c32415604ffde6fdba55f77a2f26ea9ca16351ace0cce57b1",
        )


if __name__ == "__main__":
    unittest.main()
