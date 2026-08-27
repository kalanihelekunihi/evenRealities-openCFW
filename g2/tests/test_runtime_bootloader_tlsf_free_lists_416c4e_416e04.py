from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_free_lists_416c4e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_free_lists_host.c"

STOCK = (
    (0x6C4E, 0x6CC6, "247e8e6587f838a63dfce9212d41ded0632425a60f060221b56473d4d0f2cd7a"),
    (0x6CC6, 0x6D5C, "154ffe40a56ca05bcf24241b07e08328c2db0fbc3c76b21514a79d75d5be4e20"),
    (0x6D5C, 0x6E04, "d108b1686006c53a661c34da7e449bbcecdb731643ff023f5adee1d566ca0a1e"),
)


class Block(ctypes.Structure):
    pass


BlockPointer = ctypes.POINTER(Block)
Block._fields_ = [
    ("previous_physical_block", BlockPointer),
    ("size", ctypes.c_uint32),
    ("next_free", BlockPointer),
    ("previous_free", BlockPointer),
]


BlockRow = BlockPointer * 32


class Control(ctypes.Structure):
    _fields_ = [
        ("block_null", Block),
        ("first_level_bitmap", ctypes.c_uint32),
        ("second_level_bitmap", ctypes.c_uint32 * 24),
        ("blocks", BlockRow * 24),
    ]


class BootloaderTlsfFreeListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "tlsf_free_lists.dylib" if sys.platform == "darwin" else "tlsf_free_lists.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.search = cls.lib.open_cfw_bootloader_tlsf_search_suitable_block_416c4e
        cls.search.argtypes = [ctypes.POINTER(Control), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        cls.search.restype = BlockPointer
        cls.remove = cls.lib.open_cfw_bootloader_tlsf_remove_free_block_416cc6
        cls.remove.argtypes = [ctypes.POINTER(Control), BlockPointer, ctypes.c_int, ctypes.c_int]
        cls.insert = cls.lib.open_cfw_bootloader_tlsf_insert_free_block_416d5c
        cls.insert.argtypes = [ctypes.POINTER(Control), BlockPointer, ctypes.c_int, ctypes.c_int]
        cls.reset_assert = cls.lib.open_cfw_test_tlsf_free_lists_reset_assert
        cls.assert_count = cls.lib.open_cfw_test_tlsf_free_lists_assert_count
        cls.assert_line = cls.lib.open_cfw_test_tlsf_free_lists_assert_line
        cls.assert_expression = cls.lib.open_cfw_test_tlsf_free_lists_assert_expression
        cls.assert_expression.restype = ctypes.c_size_t
        cls.assert_file = cls.lib.open_cfw_test_tlsf_free_lists_assert_file
        cls.assert_file.restype = ctypes.c_size_t
        cls.control_size = cls.lib.open_cfw_test_tlsf_free_lists_control_size
        cls.control_size.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.reset_assert()

    @staticmethod
    def pointer_value(pointer: BlockPointer) -> int | None:
        return ctypes.cast(pointer, ctypes.c_void_p).value

    @staticmethod
    def initialize(control: Control) -> None:
        sentinel = ctypes.pointer(control.block_null)
        control.block_null.next_free = sentinel
        control.block_null.previous_free = sentinel
        for first in range(24):
            for second in range(32):
                control.blocks[first][second] = sentinel

    def test_authenticated_complete_stock_entries_and_callers(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
        text = SOURCE.read_text()
        for address in (
            "0x00431A04U", "0x00431A40U", "0x00432860U", "0x00432598U",
            "0x00431A7CU", "0x0043288CU", "0x00430D3CU", "0x00415735U",
        ):
            self.assertIn(address, text)

    def test_searches_current_and_next_nonempty_classes(self):
        control = Control()
        self.initialize(control)
        current = Block()
        later = Block()
        control.blocks[2][7] = ctypes.pointer(current)
        control.second_level_bitmap[2] = 1 << 7
        control.first_level_bitmap = 1 << 2
        first = ctypes.c_int(2)
        second = ctypes.c_int(5)
        found = self.search(ctypes.byref(control), ctypes.byref(first), ctypes.byref(second))
        self.assertEqual(self.pointer_value(found), ctypes.addressof(current))
        self.assertEqual((first.value, second.value), (2, 7))

        control.blocks[4][3] = ctypes.pointer(later)
        control.second_level_bitmap[4] = 1 << 3
        control.first_level_bitmap |= 1 << 4
        first.value = 2
        second.value = 8
        found = self.search(ctypes.byref(control), ctypes.byref(first), ctypes.byref(second))
        self.assertEqual(self.pointer_value(found), ctypes.addressof(later))
        self.assertEqual((first.value, second.value), (4, 3))
        self.assertEqual(self.assert_count(), 0)

    def test_search_exhaustion_returns_null_without_rewriting_indices(self):
        control = Control()
        self.initialize(control)
        first = ctypes.c_int(6)
        second = ctypes.c_int(12)
        found = self.search(ctypes.byref(control), ctypes.byref(first), ctypes.byref(second))
        self.assertFalse(found)
        self.assertEqual((first.value, second.value), (6, 12))
        self.assertEqual(self.assert_count(), 0)

    def test_insert_and_remove_head_update_links_and_bitmaps(self):
        control = Control()
        self.initialize(control)
        first, second = 3, 11
        block = Block()
        sentinel_address = ctypes.addressof(control.block_null)

        self.insert(ctypes.byref(control), ctypes.byref(block), first, second)
        self.assertEqual(self.pointer_value(control.blocks[first][second]), ctypes.addressof(block))
        self.assertEqual(self.pointer_value(block.next_free), sentinel_address)
        self.assertEqual(self.pointer_value(block.previous_free), sentinel_address)
        self.assertEqual(self.pointer_value(control.block_null.previous_free), ctypes.addressof(block))
        self.assertEqual(control.first_level_bitmap, 1 << first)
        self.assertEqual(control.second_level_bitmap[first], 1 << second)

        self.remove(ctypes.byref(control), ctypes.byref(block), first, second)
        self.assertEqual(self.pointer_value(control.blocks[first][second]), sentinel_address)
        self.assertEqual(self.pointer_value(control.block_null.next_free), sentinel_address)
        self.assertEqual(self.pointer_value(control.block_null.previous_free), sentinel_address)
        self.assertEqual(control.first_level_bitmap, 0)
        self.assertEqual(control.second_level_bitmap[first], 0)
        self.assertEqual(self.assert_count(), 0)

    def test_non_head_removal_preserves_class_head_and_bitmaps(self):
        control = Control()
        self.initialize(control)
        first, second = 5, 9
        older = Block()
        newer = Block()
        self.insert(ctypes.byref(control), ctypes.byref(older), first, second)
        self.insert(ctypes.byref(control), ctypes.byref(newer), first, second)
        self.remove(ctypes.byref(control), ctypes.byref(older), first, second)
        self.assertEqual(self.pointer_value(control.blocks[first][second]), ctypes.addressof(newer))
        self.assertEqual(self.pointer_value(newer.next_free), ctypes.addressof(control.block_null))
        self.assertEqual(self.pointer_value(control.block_null.previous_free), ctypes.addressof(newer))
        self.assertEqual(control.first_level_bitmap & (1 << first), 1 << first)
        self.assertEqual(control.second_level_bitmap[first] & (1 << second), 1 << second)
        self.assertEqual(self.assert_count(), 0)

    def test_host_layout_and_freestanding_target_compile(self):
        self.assertEqual(self.control_size(), ctypes.sizeof(Control))
        output = Path(self.temporary.name) / "free_lists.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
