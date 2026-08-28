# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for Touch flash-row adapters."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_flash_row_adapters.c"
WRITE = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint8))
ERROR = 0x06160002


class Provider(ctypes.Structure):
    _fields_ = [("write_row", WRITE), ("context", ctypes.c_void_p)]


class TouchFlashRowAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_flash_rows.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True,
                       text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_flash_14b0_zero_rows.argtypes = [
            ctypes.POINTER(Provider), ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_touch_flash_14b0_zero_rows.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_flash_1510_copy_rows.argtypes = [
            ctypes.POINTER(Provider), ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.open_cfw_touch_flash_1510_copy_rows.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_flash_1560_copy_callback.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_zero_rows_are_128_bytes_and_ordered(self):
        calls = []
        callback = WRITE(lambda _c, address, data:
                         calls.append((address, bytes(data[:128]))) or 9)
        provider = Provider(callback, None)
        status = self.lib.open_cfw_touch_flash_14b0_zero_rows(
            ctypes.byref(provider), 0x2000, 256)
        self.assertEqual(status, 0)
        self.assertEqual([call[0] for call in calls], [0x2000, 0x2080])
        self.assertTrue(all(payload == bytes(128) for _, payload in calls))

    def test_copy_rows_advance_address_and_source(self):
        calls = []
        callback = WRITE(lambda _c, address, data:
                         calls.append((address, bytes(data[:128]))) or 7)
        provider = Provider(callback, None)
        source = (ctypes.c_uint8 * 256)(*range(256))
        status = self.lib.open_cfw_touch_flash_1510_copy_rows(
            ctypes.byref(provider), 0x3000, 256, source)
        self.assertEqual(status, 0)
        self.assertEqual(calls, [(0x3000, bytes(range(128))),
                                 (0x3080, bytes(range(128, 256)))])

    def test_non_row_length_and_missing_provider_fail_closed(self):
        self.assertEqual(self.lib.open_cfw_touch_flash_14b0_zero_rows(
            None, 0, 128), ERROR)
        callback = WRITE(lambda *_args: 0)
        provider = Provider(callback, None)
        self.assertEqual(self.lib.open_cfw_touch_flash_1510_copy_rows(
            ctypes.byref(provider), 0, 129, None), ERROR)

    def test_copy_callback_is_bounded_and_returns_zero(self):
        source = (ctypes.c_uint8 * 5)(1, 2, 3, 4, 5)
        destination = (ctypes.c_uint8 * 7)(*([0xA5] * 7))
        self.assertEqual(self.lib.open_cfw_touch_flash_1560_copy_callback(
            None, source, 5, destination), 0)
        self.assertEqual(bytes(destination), b"\x01\x02\x03\x04\x05\xA5\xA5")

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang, nm = shutil.which("clang"), shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-flash-row-b19.o"
        subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                        "-mthumb", "-ffreestanding", "-std=c11", "-Wall",
                        "-Wextra", "-Werror", "-I", str(TOUCH), "-c",
                        str(SOURCE), "-o", str(output)], check=True,
                       capture_output=True, text=True)
        listing = subprocess.run([nm, "-g", str(output)], check=True,
                                 capture_output=True, text=True).stdout
        self.assertFalse(any(len(line.split()) >= 2 and line.split()[-2] == "U"
                             for line in listing.splitlines()))


if __name__ == "__main__":
    unittest.main()
