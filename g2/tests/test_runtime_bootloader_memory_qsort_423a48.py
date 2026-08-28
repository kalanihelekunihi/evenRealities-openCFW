from __future__ import annotations

import ctypes
import hashlib
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_qsort_423a48.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_qsort_host.c"
COMPARE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


class Record(ctypes.Structure):
    _fields_ = [("key", ctypes.c_int32), ("payload", ctypes.c_uint32)]


class BootloaderMemoryQsortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("mq.dylib" if sys.platform == "darwin" else "mq.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.sort = cls.lib.open_cfw_bootloader_memory_qsort_423d08
        cls.sort.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, COMPARE]
        cls.sort.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def comparator(calls: list[tuple[int, int]]) -> COMPARE:
        @COMPARE
        def compare(left: int, right: int) -> int:
            a = ctypes.cast(left, ctypes.POINTER(Record))[0].key
            b = ctypes.cast(right, ctypes.POINTER(Record))[0].key
            calls.append((a, b))
            return (a > b) - (a < b)

        return compare

    def test_authenticated_core_wrapper_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13A48:0x13D08]).hexdigest(), "9c13dd0e980154026e6c64019ce90997dcbd5abafb79aabbbf7d3def82215bb8")
        self.assertEqual(hashlib.sha256(blob[0x13D08:0x13D20]).hexdigest(), "ebab1f26584cfab24667fa6bd4a9c63641d5676a46affda15c6478a5d697d474")
        self.assertEqual(hashlib.sha256(blob[0x13D20:0x13D58]).hexdigest(), "e4c5106b0aba4050c24d6e8afc548516c92c295bec52ed0397c029a4bad40850")

    def test_records_sort_as_whole_elements(self) -> None:
        calls: list[tuple[int, int]] = []
        values = [(7, 70), (-3, 31), (11, 110), (0, 9), (7, 71)]
        records = (Record * len(values))(*(Record(*value) for value in values))
        self.sort(records, len(records), ctypes.sizeof(Record), self.comparator(calls))
        self.assertEqual([record.key for record in records], [-3, 0, 7, 7, 11])
        self.assertEqual(sorted((record.key, record.payload) for record in records), sorted(values))
        self.assertGreater(len(calls), 0)

    def test_random_large_arrays_match_reference_order(self) -> None:
        rng = random.Random(0x423A48)
        for count in (2, 32, 33, 41, 96):
            values = [rng.randrange(-40, 41) for _ in range(count)]
            records = (Record * count)(*(Record(value, index) for index, value in enumerate(values)))
            calls: list[tuple[int, int]] = []
            self.sort(records, count, ctypes.sizeof(Record), self.comparator(calls))
            self.assertEqual([record.key for record in records], sorted(values))
            self.assertEqual(sorted(record.payload for record in records), list(range(count)))

    def test_zero_and_single_element_are_noops(self) -> None:
        calls: list[tuple[int, int]] = []
        compare = self.comparator(calls)
        records = (Record * 1)(Record(5, 99))
        self.sort(records, 0, ctypes.sizeof(Record), compare)
        self.sort(records, 1, ctypes.sizeof(Record), compare)
        self.assertEqual((records[0].key, records[0].payload), (5, 99))
        self.assertEqual(calls, [])

    def test_null_base_or_comparator_is_noop(self) -> None:
        calls: list[tuple[int, int]] = []
        compare = self.comparator(calls)
        records = (Record * 2)(Record(2, 2), Record(1, 1))
        self.sort(None, 2, ctypes.sizeof(Record), compare)
        self.sort(records, 2, ctypes.sizeof(Record), COMPARE())
        self.assertEqual([(r.key, r.payload) for r in records], [(2, 2), (1, 1)])
        self.assertEqual(calls, [])

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-mq.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
