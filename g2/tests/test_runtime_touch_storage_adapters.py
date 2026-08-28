# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch storage adapter batch 15."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_storage_adapters.c"
U8 = ctypes.c_uint8
U8P = ctypes.POINTER(U8)
INIT = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p)
READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, U8P,
                       ctypes.c_uint32, ctypes.c_void_p)
OP = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)


class Provider(ctypes.Structure):
    _fields_ = [("initialize", INIT), ("read", READ), ("context_operation", OP)]


class State(ctypes.Structure):
    _fields_ = [("descriptor", ctypes.c_uint32),
                ("provider_context", ctypes.c_void_p),
                ("counter", ctypes.c_uint32), ("initialized", ctypes.c_uint8)]


class TouchStorageAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_storage.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        "-o", str(library)], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_storage_01d8_initialize.argtypes = [
            ctypes.POINTER(State), ctypes.POINTER(Provider)]
        cls.lib.open_cfw_touch_storage_0220_read.argtypes = [
            ctypes.POINTER(State), ctypes.POINTER(Provider), ctypes.c_uint32,
            U8P, ctypes.c_uint32]
        cls.lib.open_cfw_touch_storage_02b0_context_operation.argtypes = [
            ctypes.POINTER(State), ctypes.POINTER(Provider)]
        cls.lib.open_cfw_touch_storage_02e4_increment.argtypes = [ctypes.POINTER(State)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def providers(self, init_status=0, read_status=0, op_status=0):
        callbacks = (
            INIT(lambda descriptor, _context: init_status if descriptor[0] == 0xE400 else 9),
            READ(lambda offset, destination, size, _context:
                 read_status if (offset, size, bool(destination)) == (4, 2, True) else 9),
            OP(lambda _context: op_status),
        )
        return callbacks, Provider(*callbacks)

    def test_initialize_accepts_two_provider_success_codes(self):
        for status in (0, 0x093E0004):
            state = State()
            _callbacks, provider = self.providers(init_status=status)
            self.assertEqual(self.lib.open_cfw_touch_storage_01d8_initialize(
                ctypes.byref(state), ctypes.byref(provider)), 0)
            self.assertEqual((state.descriptor, state.initialized), (0xE400, 1))
        state = State()
        _callbacks, provider = self.providers(init_status=5)
        self.assertEqual(self.lib.open_cfw_touch_storage_01d8_initialize(
            ctypes.byref(state), ctypes.byref(provider)), 1)

    def test_read_bounds_readiness_and_status_translation(self):
        state = State(initialized=1)
        destination = (U8 * 2)()
        _callbacks, provider = self.providers()
        self.assertEqual(self.lib.open_cfw_touch_storage_0220_read(
            ctypes.byref(state), ctypes.byref(provider), 4, destination, 2), 0)
        self.assertEqual(self.lib.open_cfw_touch_storage_0220_read(
            ctypes.byref(state), ctypes.byref(provider), 255, destination, 2), 4)
        state.initialized = 0
        self.assertEqual(self.lib.open_cfw_touch_storage_0220_read(
            ctypes.byref(state), ctypes.byref(provider), 4, destination, 2), 1)

    def test_context_operation_and_counter(self):
        state = State(initialized=1, counter=0xFFFFFFFF)
        _callbacks, provider = self.providers(op_status=0x093E0004)
        self.assertEqual(self.lib.open_cfw_touch_storage_02b0_context_operation(
            ctypes.byref(state), ctypes.byref(provider)), 0)
        self.lib.open_cfw_touch_storage_02e4_increment(ctypes.byref(state))
        self.assertEqual(state.counter, 0)
        state.initialized = 0
        self.assertEqual(self.lib.open_cfw_touch_storage_02b0_context_operation(
            ctypes.byref(state), ctypes.byref(provider)), 1)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-storage-batch15.o"
        subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                        "-mthumb", "-ffreestanding", "-std=c11", "-Wall",
                        "-Wextra", "-Werror", "-I", str(TOUCH), "-c",
                        str(SOURCE), "-o", str(output)], check=True,
                       capture_output=True, text=True)
        listing = subprocess.run([nm, "-g", str(output)], check=True,
                                 capture_output=True, text=True).stdout
        undefined = {line.split()[-1] for line in listing.splitlines()
                     if len(line.split()) >= 2 and line.split()[-2] == "U"}
        self.assertEqual(undefined, set())


if __name__ == "__main__":
    unittest.main()
