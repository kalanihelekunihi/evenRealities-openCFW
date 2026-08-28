# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch deferred-work batch 17."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_deferred_work.c"
ENTER = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
EXIT = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32)
NOTIFY = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint16)
LOAD = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)


class State(ctypes.Structure):
    _fields_ = [("notify_pending", ctypes.c_uint8),
                ("config_pending", ctypes.c_uint8),
                ("captured_value", ctypes.c_uint16)]


class Provider(ctypes.Structure):
    _fields_ = [("enter_critical", ENTER), ("exit_critical", EXIT),
                ("notify_value", NOTIFY), ("load_configuration", LOAD),
                ("context", ctypes.c_void_p)]


class TouchDeferredWorkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_deferred.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_deferred_0780_process.argtypes = [
            ctypes.POINTER(State), ctypes.POINTER(Provider)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_snapshots_clears_and_dispatches_in_order(self):
        calls = []
        callbacks = (
            ENTER(lambda _ctx: calls.append("enter") or 0x2A),
            EXIT(lambda _ctx, token: calls.append(("exit", token))),
            NOTIFY(lambda _ctx, value: calls.append(("notify", value))),
            LOAD(lambda _ctx: calls.append("load") or -1),
        )
        provider = Provider(*callbacks, None)
        state = State(1, 1, 0x3456)
        self.lib.open_cfw_touch_deferred_0780_process(
            ctypes.byref(state), ctypes.byref(provider))
        self.assertEqual((state.notify_pending, state.config_pending), (0, 0))
        self.assertEqual(calls, ["enter", ("exit", 0x2A),
                                 ("notify", 0x3456), "load"])

    def test_each_flag_is_independent_and_absent_provider_fails_closed(self):
        calls = []
        callbacks = (ENTER(lambda _ctx: 0), EXIT(lambda _ctx, _token: None),
                     NOTIFY(lambda _ctx, value: calls.append(value)),
                     LOAD(lambda _ctx: calls.append("load") or 0))
        provider = Provider(*callbacks, None)
        state = State(1, 0, 7)
        self.lib.open_cfw_touch_deferred_0780_process(
            ctypes.byref(state), ctypes.byref(provider))
        self.assertEqual(calls, [7])
        self.lib.open_cfw_touch_deferred_0780_process(None, None)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang, nm = shutil.which("clang"), shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-deferred-b17.o"
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
