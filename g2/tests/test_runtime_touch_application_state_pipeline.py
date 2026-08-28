# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for touch application state batch 11."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_application_state_pipeline.c"
LEAF = TOUCH / "runtime_touch_leaf_primitives.c"
FIXTURE = ROOT / "tests/fixtures/touch_application_state_pipeline_host.c"
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


def get32(buffer, offset):
    return sum(buffer[offset + index] << (8 * index) for index in range(4))


def blend(first, second, weight):
    return ((first * weight) + (second * (256 - weight))) >> 8


class PointerRegistry:
    def __init__(self, library):
        self.library = library
        self.next_token = 1
        self.keepalive = []

    def store(self, owner, offset, pointee):
        token = self.next_token
        self.next_token += 1
        if token >= 256:
            raise AssertionError("host pointer token census exhausted")
        self.keepalive.append(pointee)
        self.library.open_cfw_touch_host_register_pointer(token, pointee)
        put32(owner, offset, token)


class TouchApplicationStatePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_application_state.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-DOPEN_CFW_TOUCH_HOST_POINTER_RESOLVER",
            "-I", str(TOUCH), str(SOURCE), str(LEAF), str(FIXTURE),
            "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_host_register_pointer.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_1ebc_pack.argtypes = [U8P, U8P, U8P]
        cls.lib.open_cfw_touch_state_1ebc_pack.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_state_16d4_copy8.argtypes = [ctypes.c_uint32, U8P, U8P]
        cls.lib.open_cfw_touch_state_16e6_blend_pair.argtypes = [U8P, U8P, U8P]
        cls.lib.open_cfw_touch_state_172a_sync_records.argtypes = [U8P, U8P]
        cls.lib.open_cfw_touch_state_2568_reset_object.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_270a_update_lanes.argtypes = [U8P]
        cls.lib.open_cfw_touch_state_28c0_cap_object.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_2902_cap_enabled_object.argtypes = [ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_291e_cap_record.argtypes = [ctypes.c_uint32, ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_2956_cap_enabled_record.argtypes = [ctypes.c_uint32, ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_state_298e_status80.argtypes = [U8P]
        cls.lib.open_cfw_touch_state_298e_status80.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def make_object_graph(self, count=3):
        registry = PointerRegistry(self.lib)
        context = (U8 * 0x3A)()
        objects = (U8 * 144)()
        root = (U8 * 0x80)()
        records = (U8 * (max(count, 1) * 10))()
        registry.store(context, 12, objects)
        registry.store(objects, 0, root)
        registry.store(objects, 4, records)
        put16(objects, 0x38, count)
        return registry, context, objects, root, records

    def test_pack_all_mode_and_bypass_paths(self):
        registry, context, objects, root, records = self.make_object_graph()
        selector = (U8 * 4)()
        output = (U8 * 20)()
        auxiliary = (U8 * 0x76)()
        descriptors = (U8 * 60)()
        global_config = (U8 * 12)()
        registry.store(context, 4, global_config)
        registry.store(context, 8, auxiliary)
        registry.store(context, 16, descriptors)
        put16(selector, 2, 2)
        put16(descriptors, 0x36, 4)
        root[0x2E], root[0x2F] = 0x12, 0x34
        root[0x30], root[0x31], root[0x33] = 0x05, 0x06, 0x07
        objects[0x3A] = 2
        records[29] = 0xAB
        put32(output, 12, 0x00000044)

        for mode, flag_offset in ((1, 0x5A), (2, 0x5B), (10, 0x5C)):
            objects[0x7A] = mode
            auxiliary[flag_offset] = 1
            self.assertEqual(self.lib.open_cfw_touch_state_1ebc_pack(
                selector, output, context), 0)
            expected = 0x70C00000
            if mode == 1:
                expected |= 0x34 | (0x06 << 16) | (0xAB << 8)
            else:
                expected |= 0x12 | (0x05 << 16)
            self.assertEqual(get32(output, 16), expected)
            auxiliary[flag_offset] = 0

        self.assertEqual(get32(output, 12), 0x00030044)
        put32(global_config, 8, 0x1000)
        objects[0x7A] = 4
        self.lib.open_cfw_touch_state_1ebc_pack(selector, output, context)
        self.assertEqual(get32(output, 16), 0x00400000)

    def test_copy_and_blend_pair(self):
        source = (U8 * 8)(*range(8))
        destination = (U8 * 8)(*[0xA5] * 8)
        self.lib.open_cfw_touch_state_16d4_copy8(0, source, destination)
        self.assertEqual(bytes(destination), b"\xA5" * 8)
        self.lib.open_cfw_touch_state_16d4_copy8(2, source, destination)
        self.assertEqual(bytes(destination), bytes(source))

        config = (U8 * 0x74)()
        current = (U8 * 4)()
        history = (U8 * 4)()
        put32(config, 0x70, 2 | (64 << 16))
        put16(current, 0, 100)
        put16(current, 2, 200)
        put16(history, 0, 20)
        put16(history, 2, 40)
        self.lib.open_cfw_touch_state_16e6_blend_pair(config, current, history)
        expected = (blend(100, 20, 64), blend(200, 40, 64))
        self.assertEqual((get16(current, 0), get16(current, 2)), expected)
        self.assertEqual((get16(history, 0), get16(history, 2)), expected)

    def test_sync_existing_then_copy_new_records(self):
        registry = PointerRegistry(self.lib)
        control = (U8 * 5)()
        object_buffer = (U8 * 0x74)()
        group = (U8 * 5)()
        source = (U8 * 24)()
        destination = (U8 * 40)()
        registry.store(control, 0, source)
        registry.store(object_buffer, 0x3C, group)
        registry.store(group, 0, destination)
        control[4] = 3
        group[4] = 1
        put32(object_buffer, 0x70, 2 | (2 << 8) | (128 << 16))
        for index, values in enumerate(((100, 200), (300, 400), (500, 600))):
            put16(source, index * 8, values[0])
            put16(source, index * 8 + 2, values[1])
        put16(destination, 0, 20)
        put16(destination, 2, 40)
        self.lib.open_cfw_touch_state_172a_sync_records(control, object_buffer)
        self.assertEqual((get16(destination, 0), get16(destination, 2)), (60, 120))
        self.assertEqual(bytes(destination[16:24]), bytes(source[8:16]))
        self.assertEqual(bytes(destination[32:40]), bytes(source[16:24]))
        self.assertEqual(group[4], 3)

    def test_object_reset_modes_and_gate(self):
        for mode in (2, 4, 5, 6, 7):
            registry, context, objects, root, records = self.make_object_graph(2)
            destination = (U8 * 4)(*[0xA5] * 4)
            group = (U8 * 5)(0, 0, 0, 0, 9)
            registry.store(objects, 0x28, destination)
            registry.store(objects, 0x3C, group)
            root[0x20], root[0x23], root[0x28] = 0x66, 0xFF, 0xAA
            objects[0x7A] = 1
            objects[0x7B] = mode
            put32(objects, 0x70, 1)
            records[6], records[16] = 0xFF, 0xFF
            self.lib.open_cfw_touch_state_2568_reset_object(0, context)
            if mode == 7:
                self.assertEqual((root[0x23], records[6], group[4]), (0xFF, 0xFF, 9))
                continue
            self.assertEqual(root[0x23], 0xFE)
            self.assertEqual((records[6], records[16]), (0xFC, 0xFC))
            if mode == 6:
                self.assertEqual(bytes(destination), b"\x66" * 4)
            if 2 <= mode <= 5:
                self.assertEqual(root[0x28], 0)
                self.assertEqual(group[4], 0)
                self.assertEqual(destination[0], 0xA5 if mode == 4 else 0x66)

    def test_lane_update_matches_raw_reference(self):
        registry = PointerRegistry(self.lib)
        context = (U8 * 0x3A)()
        root = (U8 * 0x24)()
        lanes = (U8 * 20)()
        counters = (U8 * 4)(1, 0, 2, 1)
        registry.store(context, 0, root)
        registry.store(context, 4, lanes)
        registry.store(context, 0x28, counters)
        put16(context, 0x38, 2)
        put16(root, 8, 30)
        put16(root, 0x0A, 50)
        put16(root, 0x1E, 5)
        root[0x20] = 3
        root[0x23] = 0xFE
        put16(lanes, 4, 35)
        put16(lanes, 14, 60)
        lanes[6], lanes[16] = 1, 2

        expected_root = bytearray(root)
        expected_lanes = bytearray(lanes)
        expected_counters = bytearray(counters)
        expected_root[0x23] &= 0xFE
        for index in range(4):
            base = (index // 2) * 10
            mask = 2 if index & 1 else 1
            value = get16(expected_root, 0x0A if index & 1 else 8)
            delta = get16(expected_root, 0x1E)
            value = (value - delta) & 0xFFFFFFFF if expected_lanes[base + 6] & mask \
                else (value + delta) & 0xFFFFFFFF
            if expected_counters[index]:
                expected_counters[index] -= 1
            if get16(expected_lanes, base + 4) <= value:
                expected_counters[index] = expected_root[0x20]
                expected_lanes[base + 6] &= ~mask
            if expected_counters[index] == 0:
                expected_lanes[base + 6] |= mask
            if expected_lanes[base + 6] & mask:
                expected_root[0x23] |= 1

        self.lib.open_cfw_touch_state_270a_update_lanes(context)
        self.assertEqual(bytes(root), bytes(expected_root))
        self.assertEqual(bytes(lanes), bytes(expected_lanes))
        self.assertEqual(bytes(counters), bytes(expected_counters))

    def test_object_and_record_caps_with_mode_wrappers(self):
        registry, context, objects, root, records = self.make_object_graph(3)
        put16(root, 4, 100)
        put16(root, 6, 50)
        objects[0x7A] = 1
        objects[0x3A] = 1
        for index, value in enumerate((120, 70, 40)):
            put16(records, index * 10, value)
        self.lib.open_cfw_touch_state_28c0_cap_object(0, context)
        self.assertEqual([get16(records, index * 10) for index in range(3)],
                         [100, 50, 40])

        put16(records, 10, 90)
        objects[0x7B] = 7
        self.lib.open_cfw_touch_state_2956_cap_enabled_record(0, 1, context)
        self.assertEqual(get16(records, 10), 90)
        objects[0x7B] = 0
        self.lib.open_cfw_touch_state_2956_cap_enabled_record(0, 1, context)
        self.assertEqual(get16(records, 10), 50)
        put16(records, 0, 130)
        objects[0x7B] = 7
        self.lib.open_cfw_touch_state_2902_cap_enabled_object(0, context)
        self.assertEqual(get16(records, 0), 130)

    def test_status_query(self):
        registry = PointerRegistry(self.lib)
        context = (U8 * 8)()
        nested = (U8 * 12)()
        registry.store(context, 4, nested)
        for value in (0, 0x80, 0x180, 0xFFFFFFFF):
            put32(nested, 8, value)
            self.assertEqual(self.lib.open_cfw_touch_state_298e_status80(context),
                             value & 0x80)

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        objects = []
        for source in (SOURCE, LEAF):
            output = Path(self.temp.name) / (source.stem + "-batch11.o")
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
