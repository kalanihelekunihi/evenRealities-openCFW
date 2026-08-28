# SPDX-License-Identifier: MIT
"""Host/CM0+ tests for touch application and critical-section boundaries."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_application_boundary.c"
ASSEMBLY = TOUCH / "runtime_touch_critical_adapters.S"
FIXTURE = ROOT / "tests/fixtures/touch_application_boundary_host.c"


class TouchApplicationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_application_boundary.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE), str(FIXTURE),
            "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.touch_host_application_route.argtypes = [
            ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.touch_host_application_route.restype = ctypes.c_int
        cls.lib.touch_host_application_captured_entry.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_absent_provider_fails_closed(self):
        self.assertEqual(self.lib.touch_host_application_route(0, 0, 0x200), -1)
        self.assertEqual(self.lib.touch_host_application_captured_entry(),
                         0xFFFFFFFF)

    def test_two_typed_families_route_without_local_behavior(self):
        self.assertEqual(self.lib.touch_host_application_route(1, 0, 0x200), 20)
        self.assertEqual(self.lib.touch_host_application_captured_entry(), 0x200)
        self.assertEqual(self.lib.touch_host_application_route(1, 1, 0x1600), 21)
        self.assertEqual(self.lib.touch_host_application_captured_entry(), 0x1600)

    def test_invalid_family_or_unaligned_entry_fails_closed(self):
        self.assertEqual(self.lib.touch_host_application_route(1, 2, 0x200), -1)
        self.assertEqual(self.lib.touch_host_application_route(1, 1, 0x201), -1)

    def test_cortex_m0plus_c_and_assembly_compile(self):
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        for source in (SOURCE, ASSEMBLY):
            output = Path(self.temp.name) / (source.stem + ".o")
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                "-mthumb", "-ffreestanding", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
