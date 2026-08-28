# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch configuration bootstrap batch 16."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_configuration_bootstrap.c"
STORAGE = TOUCH / "runtime_touch_storage_adapters.c"
U8 = ctypes.c_uint8
U8P = ctypes.POINTER(U8)
INIT = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p)
READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, U8P, ctypes.c_uint32, ctypes.c_void_p)
OP = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
WRITE = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, U8P, ctypes.c_uint32, ctypes.c_void_p)
DELAY = ctypes.CFUNCTYPE(None, ctypes.c_uint32)


class Provider(ctypes.Structure):
    _fields_ = [("initialize", INIT), ("read", READ), ("context_operation", OP)]


class State(ctypes.Structure):
    _fields_ = [("descriptor", ctypes.c_uint32), ("provider_context", ctypes.c_void_p),
                ("counter", ctypes.c_uint32), ("initialized", ctypes.c_uint8)]


def put16(buffer, offset, value):
    buffer[offset], buffer[offset + 1] = value & 0xFF, (value >> 8) & 0xFF


def put32(buffer, offset, value):
    for index in range(4):
        buffer[offset + index] = (value >> (8 * index)) & 0xFF


class TouchConfigurationBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_bootstrap.so"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE),
                        str(STORAGE), "-o", str(library)], check=True,
                       capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_config_065c_bootstrap.argtypes = [
            ctypes.POINTER(State), ctypes.POINTER(Provider), WRITE, DELAY, U8P]
        cls.lib.open_cfw_touch_config_065c_bootstrap.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def call(self, stored=None, read_status=0, op_status=0, write_status=0):
        calls = []
        state = State()
        config = (U8 * 8)()
        init_cb = INIT(lambda _descriptor, _context: 0)

        def read(_offset, destination, _size, _context):
            if stored is not None:
                for index, value in enumerate(stored):
                    destination[index] = value
            return read_status

        read_cb = READ(read)
        op_cb = OP(lambda _context: calls.append("op") or op_status)
        write_cb = WRITE(lambda offset, source, size, _context:
                         calls.append(("write", offset, bytes(source[:size]))) or write_status)
        delay_cb = DELAY(lambda milliseconds: calls.append(("delay", milliseconds)))
        provider = Provider(init_cb, read_cb, op_cb)
        status = self.lib.open_cfw_touch_config_065c_bootstrap(
            ctypes.byref(state), ctypes.byref(provider), write_cb, delay_cb, config)
        return status, bytes(config), calls, (init_cb, read_cb, op_cb, write_cb, delay_cb)

    def test_valid_configuration_is_retained_and_zero_timeout_defaulted(self):
        stored = bytearray(8)
        put32(stored, 0, 0x45564E55)
        put16(stored, 4, 0x1234)
        status, config, calls, _callbacks = self.call(stored)
        self.assertEqual(status, 0)
        self.assertEqual(config[:6], bytes(stored[:6]))
        self.assertEqual(config[6:8], bytes((0xE8, 0x03)))
        self.assertEqual(calls, [])

    def test_missing_or_invalid_configuration_is_replaced_and_written(self):
        status, config, calls, _callbacks = self.call(read_status=9,
                                                       write_status=0x093E0004)
        self.assertEqual(status, 0)
        self.assertEqual(config, bytes((0x55, 0x4E, 0x56, 0x45, 0, 0, 0xE8, 3)))
        self.assertEqual(calls[0:2], ["op", ("delay", 10)])
        self.assertEqual(calls[2][0:2], ("write", 0))

    def test_provider_failures_are_fail_closed(self):
        self.assertEqual(self.call(read_status=9, op_status=7)[0], 2)
        self.assertEqual(self.call(read_status=9, write_status=7)[0], 3)
        self.assertEqual(self.lib.open_cfw_touch_config_065c_bootstrap(
            None, None, WRITE(), DELAY(), None), 4)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang, nm = shutil.which("clang"), shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        objects = []
        for source in (SOURCE, STORAGE):
            output = Path(self.temp.name) / (source.stem + "-b16.o")
            subprocess.run([clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                            "-mthumb", "-ffreestanding", "-std=c11", "-Wall",
                            "-Wextra", "-Werror", "-I", str(TOUCH), "-c",
                            str(source), "-o", str(output)], check=True,
                           capture_output=True, text=True)
            objects.append(output)
        defined, undefined = set(), set()
        for output in objects:
            listing = subprocess.run([nm, "-g", str(output)], check=True,
                                     capture_output=True, text=True).stdout
            for line in listing.splitlines():
                fields = line.split()
                if len(fields) >= 2 and fields[-2] == "U":
                    undefined.add(fields[-1])
                elif len(fields) >= 3 and fields[-2].upper() in {"T", "D", "B", "R"}:
                    defined.add(fields[-1])
        self.assertEqual(undefined - defined, set())


if __name__ == "__main__":
    unittest.main()
