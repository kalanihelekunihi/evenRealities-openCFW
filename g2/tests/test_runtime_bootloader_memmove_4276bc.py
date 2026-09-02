#!/usr/bin/env python3

from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memmove_4276bc.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_memmove_4276bc_host.c"


class BootloaderMemmoveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-memmove-")
        library = Path(cls.temporary.name) / "memmove.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            check=True,
        )
        cls.library = ctypes.CDLL(str(library))
        cls.move = cls.library.open_cfw_test_memmove_4276bc
        cls.move.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.move.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, destination: int, source: int, count: int) -> bytes:
        storage = (ctypes.c_uint8 * 32)(*range(32))
        base = ctypes.addressof(storage)
        returned = self.move(base + destination, base + source, count)
        self.assertEqual(returned, base + destination)
        return bytes(storage)

    def test_backward_overlap(self) -> None:
        observed = self.run_case(5, 0, 20)
        self.assertEqual(observed[5:25], bytes(range(20)))

    def test_forward_overlap(self) -> None:
        observed = self.run_case(0, 5, 20)
        self.assertEqual(observed[:20], bytes(range(5, 25)))

    def test_nonoverlap_alias_and_zero(self) -> None:
        self.assertEqual(self.run_case(20, 0, 8)[20:28], bytes(range(8)))
        self.assertEqual(self.run_case(3, 3, 12), bytes(range(32)))
        self.assertEqual(self.run_case(7, 1, 0), bytes(range(32)))

    def test_source_is_reviewable_compilable_c(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("open_cfw_bootloader_memmove_4276bc", text)
        self.assertIn("src_address < dst_address", text)
        self.assertIn("dst[byte_count] = src[byte_count]", text)
        for token in (".byte", ".short", ".word", ".inst", "__asm"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
