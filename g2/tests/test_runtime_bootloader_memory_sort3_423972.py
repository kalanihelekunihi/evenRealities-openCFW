from __future__ import annotations

import ctypes
import hashlib
import itertools
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_sort3_423972.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_sort3_host.c"
COMPARE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


class BootloaderMemorySort3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("ms3.dylib" if sys.platform == "darwin" else "ms3.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.sort3 = cls.lib.open_cfw_bootloader_memory_sort3_423972
        cls.sort3.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, COMPARE]
        cls.sort3.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_body_calls_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13972:0x139C2]).hexdigest(), "b6ec5384c9fd2cd9f993179c74e4993b5d85e6a0ea5c1b1533842d11fe4b76ff")
        self.assertEqual(hashlib.sha256(blob[0x139C2:0x13A48]).hexdigest(), "e209d49057309bdeb649246ad594a18f708db52ff4893c7aad55cad8464edc34")

    def test_all_distinct_permutations_are_sorted(self) -> None:
        @COMPARE
        def compare(left: int, right: int) -> int:
            a = ctypes.cast(left, ctypes.POINTER(ctypes.c_int32))[0]
            b = ctypes.cast(right, ctypes.POINTER(ctypes.c_int32))[0]
            return (a > b) - (a < b)

        for values in itertools.permutations((-7, 3, 19)):
            records = (ctypes.c_int32 * 3)(*values)
            self.sort3(ctypes.byref(records, 0), ctypes.byref(records, 4), ctypes.byref(records, 8), 4, compare)
            self.assertEqual(tuple(records), tuple(sorted(values)))

    def test_duplicates_and_already_sorted_records(self) -> None:
        calls: list[tuple[int, int]] = []

        @COMPARE
        def compare(left: int, right: int) -> int:
            a = ctypes.cast(left, ctypes.POINTER(ctypes.c_int32))[0]
            b = ctypes.cast(right, ctypes.POINTER(ctypes.c_int32))[0]
            calls.append((a, b))
            return (a > b) - (a < b)

        records = (ctypes.c_int32 * 3)(5, 5, 5)
        self.sort3(ctypes.byref(records, 0), ctypes.byref(records, 4), ctypes.byref(records, 8), 4, compare)
        self.assertEqual(tuple(records), (5, 5, 5))
        self.assertEqual(calls, [(5, 5), (5, 5), (5, 5)])

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-ms3.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
