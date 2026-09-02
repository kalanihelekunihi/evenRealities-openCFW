#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from __future__ import annotations

import ctypes
from pathlib import Path
import random
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/em9305/source_overlay/runtime_metaware.c"


class EM9305MetaWareProductionRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-em9305-meta-")
        library = Path(cls.temporary.name) / "libem9305-meta.dylib"
        subprocess.run(
            [
                "/usr/bin/clang", "-std=c11", "-O2", "-fPIC", "-shared",
                "-DOPEN_CFW_EM9305_HOST_TEST", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", str(SOURCE), "-o", str(library),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.library = ctypes.CDLL(str(library))
        for name in ("memmove", "memcpy"):
            function = getattr(cls.library, f"open_cfw_em9305_metaware_{name}")
            function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            function.restype = ctypes.c_void_p
        cls.library.open_cfw_em9305_metaware_memset.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t,
        ]
        cls.library.open_cfw_em9305_metaware_memset.restype = ctypes.c_void_p
        cls.library.open_cfw_em9305_metaware_udiv64.argtypes = [
            ctypes.c_uint64, ctypes.c_uint64,
        ]
        cls.library.open_cfw_em9305_metaware_udiv64.restype = ctypes.c_uint64
        cls.library.open_cfw_em9305_metaware_sdiv64.argtypes = [
            ctypes.c_int64, ctypes.c_int64,
        ]
        cls.library.open_cfw_em9305_metaware_sdiv64.restype = ctypes.c_int64
        for name in ("shift_left64", "shift_right64"):
            function = getattr(cls.library, f"open_cfw_em9305_metaware_{name}")
            function.argtypes = [ctypes.c_uint64, ctypes.c_uint32]
            function.restype = ctypes.c_uint64
        cls.library.open_cfw_em9305_metaware_stack_guard.argtypes = []
        cls.library.open_cfw_em9305_metaware_stack_guard.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_production_memory_and_arithmetic_bindings(self) -> None:
        buffer = (ctypes.c_ubyte * 96)(*range(96))
        returned = self.library.open_cfw_em9305_metaware_memmove(
            ctypes.byref(buffer, 9), ctypes.byref(buffer, 3), 61
        )
        self.assertEqual(returned, ctypes.addressof(buffer) + 9)
        expected = bytearray(range(96))
        expected[9:70] = bytes(range(3, 64))
        self.assertEqual(bytes(buffer), bytes(expected))

        destination = (ctypes.c_ubyte * 64)()
        self.library.open_cfw_em9305_metaware_memset(destination, 0x1ab, 64)
        self.assertEqual(bytes(destination), b"\xab" * 64)

        rng = random.Random(0x302748)
        for _ in range(256):
            dividend = rng.getrandbits(64)
            divisor = rng.getrandbits(64)
            self.assertEqual(
                self.library.open_cfw_em9305_metaware_udiv64(dividend, divisor),
                dividend // divisor,
            )
        value = 0x0123456789ABCDEF
        for count in (0, 1, 31, 32, 63, 64, 127):
            shift = count & 63
            self.assertEqual(
                self.library.open_cfw_em9305_metaware_shift_left64(value, count),
                (value << shift) & ((1 << 64) - 1),
            )
            self.assertEqual(
                self.library.open_cfw_em9305_metaware_shift_right64(value, count),
                value >> shift,
            )

    def test_production_stack_guard_uses_inclusive_limits_and_traps(self) -> None:
        stack_pointer = ctypes.c_size_t.in_dll(
            self.library, "open_cfw_em9305_host_stack_pointer"
        )
        trap_count = ctypes.c_uint32.in_dll(
            self.library, "open_cfw_em9305_host_stack_trap_count"
        )
        stack_pointer.value = 0x0080E978
        trap_count.value = 0
        self.library.open_cfw_em9305_metaware_stack_guard()
        self.assertEqual(trap_count.value, 0)
        stack_pointer.value = 0x0080F979
        self.library.open_cfw_em9305_metaware_stack_guard()
        self.assertEqual(trap_count.value, 1)

    def test_production_binding_is_c_without_raw_arc_encodings(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("__builtin_trap()", source)
        self.assertIn("runtime_metaware_helpers_candidate.c", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)


if __name__ == "__main__":
    unittest.main()
