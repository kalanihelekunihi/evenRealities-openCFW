from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_heap_sift_4239c2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_heap_sift_host.c"
COMPARE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


class BootloaderMemoryHeapSiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("mhs.dylib" if sys.platform == "darwin" else "mhs.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.sift = cls.lib.open_cfw_bootloader_memory_heap_sift_4239c2
        cls.sift.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, COMPARE]
        cls.sift.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def comparator(calls: list[tuple[int, int]]) -> COMPARE:
        @COMPARE
        def compare(left: int, right: int) -> int:
            a = ctypes.cast(left, ctypes.POINTER(ctypes.c_int32))[0]
            b = ctypes.cast(right, ctypes.POINTER(ctypes.c_int32))[0]
            calls.append((a, b))
            return (a > b) - (a < b)

        return compare

    def test_authenticated_body_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x139C2:0x13A48]).hexdigest(), "e209d49057309bdeb649246ad594a18f708db52ff4893c7aad55cad8464edc34")
        self.assertEqual(hashlib.sha256(blob[0x13A48:0x13BC0]).hexdigest(), "a61cc0c510adb8f1de6b1938e1f45e8add73726d38ee5b736da8648b6ab855d4")

    def test_left_only_child_uses_exclusive_count_boundary(self) -> None:
        calls: list[tuple[int, int]] = []
        records = (ctypes.c_int32 * 2)(1, 9)
        self.sift(records, 0, 2, 4, self.comparator(calls))
        self.assertEqual(tuple(records), (9, 1))
        self.assertEqual(calls, [(1, 9)])

    def test_both_children_select_larger_then_descend(self) -> None:
        calls: list[tuple[int, int]] = []
        records = (ctypes.c_int32 * 7)(1, 8, 9, 6, 7, 4, 5)
        self.sift(records, 0, 7, 4, self.comparator(calls))
        self.assertEqual(tuple(records), (9, 8, 5, 6, 7, 4, 1))
        self.assertEqual(calls, [(9, 8), (5, 4), (1, 5)])

    def test_upward_repair_restores_overextended_descent(self) -> None:
        calls: list[tuple[int, int]] = []
        records = (ctypes.c_int32 * 7)(10, 8, 9, 6, 7, 4, 5)
        self.sift(records, 0, 7, 4, self.comparator(calls))
        self.assertEqual(tuple(records), (10, 8, 9, 6, 7, 4, 5))
        self.assertEqual(calls, [(9, 8), (5, 4), (10, 5), (10, 9)])

    def test_subtree_start_preserves_unrelated_records(self) -> None:
        calls: list[tuple[int, int]] = []
        records = (ctypes.c_int32 * 8)(99, 1, 50, 7, 8, 40, 30, 6)
        self.sift(records, 1, 8, 4, self.comparator(calls))
        self.assertEqual(tuple(records), (99, 8, 50, 7, 1, 40, 30, 6))
        self.assertEqual(calls, [(8, 7), (1, 8)])

    def test_empty_descent_is_noop_without_comparator(self) -> None:
        calls: list[tuple[int, int]] = []
        records = (ctypes.c_int32 * 3)(7, 6, 5)
        self.sift(records, 2, 3, 4, self.comparator(calls))
        self.assertEqual(tuple(records), (7, 6, 5))
        self.assertEqual(calls, [])

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-mhs.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
