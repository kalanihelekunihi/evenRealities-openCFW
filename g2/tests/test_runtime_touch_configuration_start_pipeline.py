# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch configuration/start batch 14."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_configuration_start_pipeline.c"
FIXTURE = ROOT / "tests/fixtures/touch_application_state_pipeline_host.c"
U8 = ctypes.c_uint8
U8P = ctypes.POINTER(U8)
CAPTURE = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32)
EVENT = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint32, U8P)


class Providers(ctypes.Structure):
    _fields_ = [("capture", CAPTURE), ("event", EVENT)]


def put16(buffer, offset, value):
    buffer[offset] = value & 0xFF
    buffer[offset + 1] = (value >> 8) & 0xFF


def get16(buffer, offset):
    return buffer[offset] | (buffer[offset + 1] << 8)


def put32(buffer, offset, value):
    for index in range(4):
        buffer[offset + index] = (value >> (8 * index)) & 0xFF


def get32(buffer, offset):
    return sum(buffer[offset + index] << (8 * index) for index in range(4))


class PointerRegistry:
    def __init__(self, library):
        self.library = library
        self.token = 1
        self.keepalive = []

    def store(self, owner, offset, pointee):
        token = self.token
        self.token += 1
        self.keepalive.append(pointee)
        self.library.open_cfw_touch_host_register_pointer(token, pointee)
        put32(owner, offset, token)


class TouchConfigurationStartPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_configuration_start.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-DOPEN_CFW_TOUCH_HOST_POINTER_RESOLVER",
            "-I", str(TOUCH), str(SOURCE), str(FIXTURE), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_host_register_pointer.argtypes = [ctypes.c_uint32, U8P]
        for name in ("open_cfw_touch_config_1944_start",
                     "open_cfw_touch_config_1972_start_wrapper",
                     "open_cfw_touch_config_197c_initialize"):
            function = getattr(cls.lib, name)
            function.argtypes = [U8P, ctypes.POINTER(Providers)]
            function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def make_object(self):
        registry = PointerRegistry(self.lib)
        object_buffer = (U8 * 0x10)()
        root = (U8 * 0x40)()
        state = (U8 * 0x76)()
        holder = (U8 * 4)()
        records = (U8 * (3 * 0x3C))()
        capture_context = (U8 * 8)()
        busy = (U8 * 1)()
        registry.store(object_buffer, 0, root)
        registry.store(object_buffer, 8, state)
        registry.store(object_buffer, 0x0C, holder)
        registry.store(holder, 0, records)
        registry.store(root, 8, capture_context)
        registry.store(capture_context, 4, busy)
        put32(capture_context, 0, 0x12345678)
        return (registry, object_buffer, root, state, records,
                capture_context, busy)

    def test_start_fail_closed_and_provider_statuses(self):
        (_registry, obj, _root, _state, _records, _context,
         busy) = self.make_object()
        calls = []

        def capture(base, key):
            calls.append(("capture", base, key))
            return 0

        def event(number, _object):
            calls.append(("event", number))
            return 0x35

        callbacks = (CAPTURE(capture), EVENT(event))
        providers = Providers(*callbacks)
        busy[0] = 1
        self.assertEqual(self.lib.open_cfw_touch_config_1944_start(
            obj, ctypes.byref(providers)), 0x80)
        self.assertEqual(calls, [])
        busy[0] = 0
        self.assertEqual(self.lib.open_cfw_touch_config_1972_start_wrapper(
            obj, ctypes.byref(providers)), 0x35)
        self.assertEqual(calls, [("capture", 0x12345678, 2), ("event", 1)])

        failing_capture = CAPTURE(lambda _base, _key: 7)
        providers = Providers(failing_capture, callbacks[1])
        self.assertEqual(self.lib.open_cfw_touch_config_1944_start(
            obj, ctypes.byref(providers)), 8)

    def test_initializer_reconstructs_argument_relative_configuration(self):
        (_registry, obj, root, state, records, _context,
         _busy) = self.make_object()
        for offset, value in ((0x16, 0x123), (0x18, 0x456), (0x1C, 0x111),
                              (0x1E, 0x222), (0x20, 0x333), (0x22, 0x444)):
            put16(root, offset, value)
        root[0x2D], root[0x2F], root[0x31] = 0x2D, 0x2F, 0x31
        root[0x34], root[0x35] = 0x34, 0x35
        put16(records, 4, 0)
        put16(records, 6, 1)
        put16(records, 0x3C + 4, 1)
        put16(records, 0x3C + 6, 0)
        events = []
        capture_cb = CAPTURE(lambda _base, _key: 0)

        def event(number, _object):
            events.append(number)
            return 0x44 if number == 0 else 0

        event_cb = EVENT(event)
        providers = Providers(capture_cb, event_cb)
        self.assertEqual(self.lib.open_cfw_touch_config_197c_initialize(
            obj, ctypes.byref(providers)), 0x44)
        self.assertEqual(events, [0])
        self.assertEqual((state[0x57], state[0x58], state[0x59]),
                         (0x2F, 0x2D, 0x31))
        self.assertEqual((get16(state, 0x30), get16(state, 0x32)),
                         (0x123, 0x456))
        self.assertEqual((get16(state, 0x3E), get16(state, 0x40),
                          get16(state, 0x42), get16(state, 0x44)),
                         (0x111, 0x222, 0x333, 0x444))
        self.assertEqual(get32(state, 0x2C), 0x28F)
        self.assertEqual(get32(state, 0x24), 0xF424)
        self.assertEqual(get16(state, 0x3C), 0x084C)
        self.assertEqual(get16(state, 0x4A), 0x20)
        self.assertEqual(tuple(state[i] for i in range(0x4D, 0x55)),
                         (3, 0, 0xFF, 0x8E, 1, 0, 0x34, 0x35))
        self.assertEqual(tuple(state[i] for i in range(0x5A, 0x61)),
                         (3, 0, 0, 6, 4, 10, 3))
        self.assertEqual((records[0x23], records[0x3C + 0x23],
                          records[2 * 0x3C + 0x23]),
                         (0x0E, 0x16, 0x1E))

    def test_initializer_success_continues_to_start(self):
        (_registry, obj, _root, _state, _records, _context,
         _busy) = self.make_object()
        events = []
        capture_cb = CAPTURE(lambda _base, _key: 0)
        event_cb = EVENT(lambda number, _object: events.append(number) or 0)
        providers = Providers(capture_cb, event_cb)
        self.assertEqual(self.lib.open_cfw_touch_config_197c_initialize(
            obj, ctypes.byref(providers)), 0)
        self.assertEqual(events, [0, 1])

    def test_null_contracts_fail_closed(self):
        self.assertEqual(self.lib.open_cfw_touch_config_197c_initialize(None, None), 1)
        self.assertEqual(self.lib.open_cfw_touch_config_1944_start(None, None), 0x80)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        output = Path(self.temp.name) / "touch-config-batch14.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True, text=True)
        listing = subprocess.run([nm, "-g", str(output)], check=True,
                                 capture_output=True, text=True).stdout
        undefined = {line.split()[-1] for line in listing.splitlines()
                     if len(line.split()) >= 2 and line.split()[-2] == "U"}
        self.assertEqual(undefined, set())


if __name__ == "__main__":
    unittest.main()
