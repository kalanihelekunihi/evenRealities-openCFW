# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for the closed Touch startup routines."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_startup_closed.c"
DISABLE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32,
                           ctypes.c_uint32)
SET_INT = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32,
                           ctypes.c_uint32, ctypes.c_uint32)
SET_FRAC = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)
ENABLE = DISABLE
ASSIGN = SET_INT


class Record(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 80)]


class Provider(ctypes.Structure):
    _fields_ = [("disable_divider", DISABLE),
                ("set_integer_divider", SET_INT),
                ("set_fractional_divider", SET_FRAC),
                ("enable_divider", ENABLE), ("assign_divider", ASSIGN),
                ("context", ctypes.c_void_p)]


class TouchStartupClosedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_startup_closed.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True,
                       text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_startup_0d4c_initialize.argtypes = [
            ctypes.POINTER(Record), ctypes.POINTER(ctypes.c_uint16)]
        cls.lib.open_cfw_touch_startup_11d0_configure_dividers.argtypes = [
            ctypes.POINTER(Provider)]
        cls.lib.open_cfw_touch_startup_1228_assign_divider.argtypes = [
            ctypes.POINTER(Provider)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_record_is_zeroed_and_timeout_is_defaulted_or_retained(self):
        for supplied, expected in ((0, 1000), (0x3456, 0x3456)):
            record = Record((ctypes.c_uint8 * 80)(*([0xA5] * 80)))
            value = ctypes.c_uint16(supplied)
            self.lib.open_cfw_touch_startup_0d4c_initialize(
                ctypes.byref(record), ctypes.byref(value))
            self.assertEqual(record.bytes[0] | (record.bytes[1] << 8), expected)
            self.assertEqual(bytes(record.bytes[2:]), bytes(78))

    def test_exact_divider_sequence_and_assign(self):
        calls = []
        callbacks = (
            DISABLE(lambda _c, t, i: calls.append(("disable", t, i))),
            SET_INT(lambda _c, t, i, d: calls.append(("integer", t, i, d))),
            SET_FRAC(lambda _c, t, i, d, f:
                     calls.append(("fractional", t, i, d, f))),
            ENABLE(lambda _c, t, i: calls.append(("enable", t, i))),
            ASSIGN(lambda _c, d, t, i: calls.append(("assign", d, t, i))),
        )
        provider = Provider(*callbacks, None)
        self.lib.open_cfw_touch_startup_11d0_configure_dividers(
            ctypes.byref(provider))
        self.lib.open_cfw_touch_startup_1228_assign_divider(
            ctypes.byref(provider))
        self.assertEqual(calls, [
            ("disable", 1, 1), ("integer", 1, 1, 3), ("enable", 1, 1),
            ("disable", 2, 0), ("fractional", 2, 0, 0x33, 3),
            ("enable", 2, 0), ("disable", 3, 0),
            ("fractional", 3, 0, 0x33, 3), ("enable", 3, 0),
            ("assign", 1, 1, 1),
        ])

    def test_missing_providers_fail_closed(self):
        self.lib.open_cfw_touch_startup_0d4c_initialize(None, None)
        self.lib.open_cfw_touch_startup_11d0_configure_dividers(None)
        self.lib.open_cfw_touch_startup_1228_assign_divider(None)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang, nm = shutil.which("clang"), shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-startup-b18.o"
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
