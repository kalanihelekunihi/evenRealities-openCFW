# SPDX-License-Identifier: MIT
"""Host and CM0+ tests for instruction-established touch leaf primitives."""

import ctypes
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_leaf_primitives.c"
FIXTURE = ROOT / "tests/fixtures/touch_leaf_primitives_host.c"


class TouchLeafPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_leaf_primitives.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE), str(FIXTURE),
            "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.touch_host_leaf_passthrough.argtypes = [ctypes.c_uint32] * 2
        cls.lib.touch_host_leaf_passthrough.restype = ctypes.c_uint32
        cls.lib.touch_host_leaf_constant.argtypes = [ctypes.c_uint32] * 5
        cls.lib.touch_host_leaf_constant.restype = ctypes.c_uint32
        for name in ("open_cfw_touch_leaf_1490_bounded_sum",
                     "open_cfw_touch_leaf_1ca8_median3",
                     "open_cfw_touch_leaf_1cde_blend_u8",
                     "open_cfw_touch_leaf_2228_mode_scale"):
            function = getattr(cls.lib, name)
            function.argtypes = [ctypes.c_uint32] * 3
            function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_six_passthrough_register_bodies(self):
        for entry in (0x1226, 0x1236, 0x12A4, 0x1366, 0x1370, 0x1418):
            for value in (0, 1, 0x80000000, 0xFFFFFFFF):
                self.assertEqual(self.lib.touch_host_leaf_passthrough(entry, value), value)

    def test_six_constant_register_bodies(self):
        expected = {0x1480: 1, 0x1484: 128, 0x1488: 128,
                    0x148C: 0, 0x14AA: 0, 0x1AB4: 0}
        for entry, value in expected.items():
            self.assertEqual(
                self.lib.touch_host_leaf_constant(
                    entry, 0xFFFFFFFF, 0x12345678, 0xABCDEF01, 0x80000000),
                value,
            )

    def test_bounded_modular_sum_matches_target_branches(self):
        function = self.lib.open_cfw_touch_leaf_1490_bounded_sum
        cases = [
            (0, 0, 0), (0, 1, 0), (0, 1, 0xFFFF),
            (0, 1, 0x10000), (0, 0xFFFFFFFF, 1),
        ]
        for r0, r1, r2 in cases:
            expected = int(r1 != 0 and ((r1 + r2) & 0xFFFFFFFF) <= 0x10000)
            self.assertEqual(function(r0, r1, r2), expected)

    def test_median_matches_unsigned_register_ordering(self):
        function = self.lib.open_cfw_touch_leaf_1ca8_median3
        rng = random.Random(0x1CA8)
        for _ in range(256):
            values = [rng.getrandbits(32) for _ in range(3)]
            self.assertEqual(function(*values), sorted(values)[1])

    def test_blend_matches_modulo_32_bit_target_arithmetic(self):
        function = self.lib.open_cfw_touch_leaf_1cde_blend_u8
        rng = random.Random(0x1CDE)
        for _ in range(256):
            r0, r1, r2 = (rng.getrandbits(32) for _ in range(3))
            product0 = (r0 * r2) & 0xFFFFFFFF
            weight1 = (256 - r2) & 0xFFFFFFFF
            product1 = (r1 * weight1) & 0xFFFFFFFF
            expected = ((product0 + product1) & 0xFFFFFFFF) >> 8
            self.assertEqual(function(r0, r1, r2), expected)

    def test_mode_scale_matches_target_branch_partition(self):
        function = self.lib.open_cfw_touch_leaf_2228_mode_scale
        for mode in (0, 1, 2, 10, 11):
            for flags in range(8):
                for value in (0, 1, 0x80, 0xFFFFFFFF):
                    if (flags & 3) != 2:
                        expected = value
                    elif mode in (1, 10):
                        expected = value >> 2
                    else:
                        expected = value >> 1
                    self.assertEqual(function(mode, flags, value), expected)

    def test_cortex_m0plus_compile(self):
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch_leaf_primitives.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
