# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for terminal Touch wrappers."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_terminal_wrappers.c"


class Context(ctypes.Structure):
    pass


RESET = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32,
                         ctypes.POINTER(Context))
CAPSENSE = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32)
Context._fields_ = [("object", ctypes.POINTER(ctypes.c_uint8)),
                    ("control", ctypes.POINTER(ctypes.c_uint32))]


class Provider(ctypes.Structure):
    _fields_ = [("reset_object", RESET), ("capsense_call", CAPSENSE),
                ("context", ctypes.c_void_p)]


class TouchTerminalWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_terminal.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True,
                       text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_terminal_1368_passthrough.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_terminal_25f8_reset_three.argtypes = [
            ctypes.POINTER(Context), ctypes.POINTER(Provider)]
        cls.lib.open_cfw_touch_terminal_297a_conditional_call.argtypes = [
            ctypes.POINTER(Provider), ctypes.c_uint32]
        cls.lib.open_cfw_touch_terminal_297a_conditional_call.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_passthrough_preserves_value(self):
        self.assertEqual(self.lib.open_cfw_touch_terminal_1368_passthrough(
            0xA5A55A5A), 0xA5A55A5A)

    def test_reset_clears_exact_bit_and_visits_two_one_zero(self):
        calls = []
        control = (ctypes.c_uint32 * 3)(0, 0, 0xFFFFFFFF)
        context = Context(None, control)
        callbacks = (
            RESET(lambda _p, index, _c: calls.append(index)),
            CAPSENSE(lambda *_args: 0),
        )
        provider = Provider(*callbacks, None)
        self.lib.open_cfw_touch_terminal_25f8_reset_three(
            ctypes.byref(context), ctypes.byref(provider))
        self.assertEqual(control[2], 0xFFFFFBFF)
        self.assertEqual(calls, [2, 1, 0])

    def test_conditional_provider_call(self):
        calls = []
        callbacks = (
            RESET(lambda *_args: None),
            CAPSENSE(lambda _p, a, b, c: calls.append((a, b, c)) or 9),
        )
        provider = Provider(*callbacks, None)
        self.assertEqual(self.lib.open_cfw_touch_terminal_297a_conditional_call(
            ctypes.byref(provider), 0), 1)
        self.assertEqual(self.lib.open_cfw_touch_terminal_297a_conditional_call(
            ctypes.byref(provider), 7), 9)
        self.assertEqual(calls, [(0, 5, 7)])

    def test_missing_provider_fails_closed(self):
        self.lib.open_cfw_touch_terminal_25f8_reset_three(None, None)
        self.assertEqual(self.lib.open_cfw_touch_terminal_297a_conditional_call(
            None, 4), 0)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang, nm = shutil.which("clang"), shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-terminal-b20.o"
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
