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
SOURCE = COMPONENT_ROOT / "mram_initialize_records.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "mram_initialize_records_host.c"
)


class MramInitializeRecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_initialize_records.dylib"
            if sys.platform == "darwin"
            else "mram_initialize_records.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_mram_initialize_reset
        cls.initialize = cls.loaded.open_cfw_mram_initialize_records
        cls.initialize.argtypes = []
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def word(self, name: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(self.loaded, name)

    def test_calls_source_cluster_and_dumps_all_records_in_order(
        self,
    ) -> None:
        self.reset()
        records = (ctypes.c_ubyte * 2000).in_dll(
            self.loaded,
            "open_cfw_test_mram_initialize_records",
        )
        self.word(
            "open_cfw_test_mram_initialize_cache_result"
        ).value = 0xDEADBEEF

        self.initialize()

        order = (ctypes.c_uint * 16).in_dll(
            self.loaded,
            "open_cfw_test_mram_initialize_order",
        )
        dump_records = (ctypes.c_size_t * 10).in_dll(
            self.loaded,
            "open_cfw_test_mram_initialize_dump_records",
        )
        dump_indices = (ctypes.c_uint * 10).in_dll(
            self.loaded,
            "open_cfw_test_mram_initialize_dump_indices",
        )
        self.assertEqual(list(order)[:13], list(range(1, 14)))
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_initialize_cache_range"
            ).value,
            0,
        )
        self.assertEqual(
            self.word(
                "open_cfw_test_mram_initialize_cache_all"
            ).value,
            1,
        )
        self.assertEqual(
            ctypes.c_void_p.in_dll(
                self.loaded,
                "open_cfw_test_mram_initialize_load_records",
            ).value,
            ctypes.addressof(records),
        )
        self.assertEqual(
            list(dump_records),
            [
                ctypes.addressof(records) + index * 200
                for index in range(10)
            ],
        )
        self.assertEqual(list(dump_indices), list(range(10)))

    def test_source_and_fixture_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "965b6e0b3ba80677a4c0c1c2501e80ebe9b87a5f3c3576b7a13471cf08d06984",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "795d5e69d20f4a77a48872901c81c28c4958552132c5f31b45adc5a012b99612",
        )


if __name__ == "__main__":
    unittest.main()
