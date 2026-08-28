# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch selection/update batch 13."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SELECT = TOUCH / "runtime_touch_selection_update_pipeline.c"
STATE = TOUCH / "runtime_touch_application_state_pipeline.c"
LEAF = TOUCH / "runtime_touch_leaf_primitives.c"
FIXTURE = ROOT / "tests/fixtures/touch_application_state_pipeline_host.c"
SOURCES = (SELECT, STATE, LEAF)
U8 = ctypes.c_uint8
U8P = ctypes.POINTER(U8)


def put16(buffer, offset, value):
    buffer[offset] = value & 0xFF
    buffer[offset + 1] = (value >> 8) & 0xFF


def get16(buffer, offset):
    return buffer[offset] | (buffer[offset + 1] << 8)


def put32(buffer, offset, value):
    for index in range(4):
        buffer[offset + index] = (value >> (8 * index)) & 0xFF


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


class TouchSelectionUpdatePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_selection_update.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-DOPEN_CFW_TOUCH_HOST_POINTER_RESOLVER",
            "-I", str(TOUCH), *(str(source) for source in SOURCES),
            str(FIXTURE), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_host_register_pointer.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_select_15cc_peak.argtypes = [U8P, U8P]
        cls.lib.open_cfw_touch_select_2794_update.argtypes = [U8P]
        cls.lib.open_cfw_touch_select_28a2_dispatch.argtypes = [U8P]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def make_object(self, values=(10, 20, 15)):
        registry = PointerRegistry(self.lib)
        object_buffer = (U8 * 0x7C)()
        records = (U8 * 30)()
        registry.store(object_buffer, 4, records)
        put16(object_buffer, 0x38, 3)
        put32(object_buffer, 0x30, 1)
        put16(object_buffer, 0x34, 3)
        for index, value in enumerate(values):
            put16(records, index * 10 + 4, value)
        return registry, object_buffer, records

    def test_peak_selection_positive_and_negative_correction(self):
        for values, expected in (((10, 20, 15), 2), ((15, 20, 10), 1)):
            registry, object_buffer, _records = self.make_object(values)
            result = (U8 * 5)()
            destination = (U8 * 2)()
            registry.store(result, 0, destination)
            self.lib.open_cfw_touch_select_15cc_peak(result, object_buffer)
            self.assertEqual(result[4], 1)
            self.assertEqual(get16(destination, 0), expected)

    def test_peak_selection_disabled_and_empty(self):
        registry, object_buffer, records = self.make_object((0, 0, 0))
        result = (U8 * 5)(0, 0, 0, 0, 0xA5)
        destination = (U8 * 2)()
        registry.store(result, 0, destination)
        self.lib.open_cfw_touch_select_15cc_peak(result, object_buffer)
        self.assertEqual(result[4], 0)
        put32(object_buffer, 0x30, 0)
        result[4] = 0xA5
        put16(records, 4, 20)
        self.lib.open_cfw_touch_select_15cc_peak(result, object_buffer)
        self.assertEqual(result[4], 0xA5)

    def test_update_selects_and_copies_local_result(self):
        registry, object_buffer, records = self.make_object((10, 20, 15))
        root = (U8 * 0x2C)()
        counter = (U8 * 1)(0)
        destination = (U8 * 8)()
        registry.store(object_buffer, 0, root)
        registry.store(object_buffer, 0x28, counter)
        registry.store(root, 0x24, destination)
        object_buffer[0x7B] = 2
        put32(object_buffer, 0x70, 0)
        put16(root, 8, 0)
        put16(root, 0x1E, 0)
        root[0x20] = 3
        for index in range(3):
            put16(records, index * 10 + 4, (10, 20, 15)[index])
        self.lib.open_cfw_touch_select_2794_update(object_buffer)
        self.assertEqual(root[0x23] & 1, 1)
        self.assertEqual(root[0x28], 1)
        self.assertEqual(get16(destination, 0), 2)

    def test_dispatch_modes(self):
        registry, object_buffer, records = self.make_object((10, 20, 15))
        root = (U8 * 0x2C)()
        counter = (U8 * 1)(0)
        destination = (U8 * 8)()
        registry.store(object_buffer, 0, root)
        registry.store(object_buffer, 0x28, counter)
        registry.store(root, 0x24, destination)
        object_buffer[0x7B] = 4
        before = bytes(object_buffer), bytes(root), bytes(records)
        self.lib.open_cfw_touch_select_28a2_dispatch(object_buffer)
        self.assertEqual((bytes(object_buffer), bytes(root), bytes(records)), before)
        object_buffer[0x7B] = 2
        self.lib.open_cfw_touch_select_28a2_dispatch(object_buffer)
        self.assertEqual(root[0x28], 1)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        objects = []
        for source in SOURCES:
            output = Path(self.temp.name) / (source.stem + "-batch13.o")
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], check=True, capture_output=True, text=True)
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
