# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for the clean-room CAPSENSE provider boundary."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_capsense_provider.c"
FIXTURE = ROOT / "tests/fixtures/touch_capsense_provider_host.c"


class TouchCapsenseProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_capsense_provider.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE), str(FIXTURE),
            "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.touch_host_capsense_route.argtypes = [ctypes.c_int, ctypes.c_uint32]
        cls.lib.touch_host_capsense_route.restype = ctypes.c_int
        cls.lib.touch_host_capsense_captured_operation.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_missing_provider_fails_closed(self):
        self.assertEqual(self.lib.touch_host_capsense_route(0, 1), -1)
        self.assertEqual(self.lib.touch_host_capsense_captured_operation(),
                         0xFFFFFFFF)

    def test_valid_operation_routes_without_local_semantics(self):
        self.assertEqual(self.lib.touch_host_capsense_route(1, 3), 17)
        self.assertEqual(self.lib.touch_host_capsense_captured_operation(), 3)

    def test_unknown_operation_fails_closed(self):
        self.assertEqual(self.lib.touch_host_capsense_route(1, 5), -1)
        self.assertEqual(self.lib.touch_host_capsense_captured_operation(),
                         0xFFFFFFFF)

    def test_cortex_m0plus_compilation(self):
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "capsense-provider.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
