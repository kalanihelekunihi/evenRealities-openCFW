# SPDX-License-Identifier: MIT
"""Host behavior and CM0+ closure tests for touch source batch 10."""

import ctypes
import itertools
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCES = [
    TOUCH / "runtime_touch_closed_record_pipeline.c",
    TOUCH / "runtime_touch_leaf_primitives.c",
    TOUCH / "runtime_touch_record_primitives.c",
]
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


def store_pointer(buffer, offset, pointee):
    value = ctypes.c_void_p(ctypes.addressof(pointee))
    ctypes.memmove(ctypes.addressof(buffer) + offset,
                   ctypes.byref(value), ctypes.sizeof(value))


def pointer_at(buffer, offset=0):
    return ctypes.cast(ctypes.byref(buffer, offset), U8P)


def blend(first, second, weight):
    return ((first * weight) + (second * ((256 - weight) & 0xFFFFFFFF))) >> 8


class TouchClosedRecordPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_closed_record_pipeline.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH),
            *(str(source) for source in SOURCES), "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_pipeline_1ac4_reset_one.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_pipeline_1aec_reset_object.argtypes = [
            ctypes.c_uint32, U8P]
        cls.lib.open_cfw_touch_pipeline_1b1c_reset_three.argtypes = [U8P]
        cls.lib.open_cfw_touch_pipeline_1cc2_median_shift.argtypes = [U8P, U8P, U8P]
        cls.lib.open_cfw_touch_pipeline_1cee_update.argtypes = [
            U8P, U8P, U8P, ctypes.POINTER(U8P)]
        cls.lib.open_cfw_touch_pipeline_1cee_update.restype = ctypes.c_uint32
        cls.lib.open_cfw_touch_pipeline_1d54_blend.argtypes = [U8P, U8P, U8P, U8P]
        cls.lib.open_cfw_touch_pipeline_1da0_filter_chain.argtypes = [U8P, U8P, U8P, U8P]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def make_graph(counts=(2, 3, 1), modes=(0, 0, 0)):
        pointer_size = ctypes.sizeof(ctypes.c_void_p)
        context = (U8 * (12 + pointer_size))()
        objects = (U8 * (3 * 144))()
        records = []
        for object_index, (count, mode) in enumerate(zip(counts, modes)):
            record = (U8 * (max(count, 1) * 10))()
            records.append(record)
            base = object_index * 144
            store_pointer(objects, base + 4, record)
            put16(objects, base + 0x38, count)
            objects[base + 0x7B] = mode
            for record_index in range(max(count, 1)):
                offset = record_index * 10
                put16(record, offset, 0x1200 + object_index * 0x100 + record_index)
                put16(record, offset + 2, 0xFFFF)
                record[offset + 7] = 0xA5
                record[offset + 8] = 0x5A
        store_pointer(context, 12, objects)
        return context, objects, records

    def test_pointer_graph_reset_one_and_object_mode_gate(self):
        context, _objects, records = self.make_graph(modes=(0, 7, 0))
        self.lib.open_cfw_touch_pipeline_1ac4_reset_one(0, 1, context)
        self.assertEqual(get16(records[0], 12), get16(records[0], 10))
        self.assertEqual((records[0][17], records[0][18]), (0, 0))
        self.assertEqual(get16(records[0], 2), 0xFFFF)

        self.lib.open_cfw_touch_pipeline_1aec_reset_object(1, context)
        self.assertTrue(all(records[1][index * 10 + 7] == 0xA5
                            for index in range(3)))
        self.lib.open_cfw_touch_pipeline_1aec_reset_object(0, context)
        self.assertTrue(all(records[0][index * 10 + 7] == 0
                            for index in range(2)))

    def test_three_object_reset_cascade(self):
        context, _objects, records = self.make_graph()
        self.lib.open_cfw_touch_pipeline_1b1c_reset_three(context)
        for record in records:
            for offset in range(0, len(record), 10):
                self.assertEqual(get16(record, offset + 2), get16(record, offset))
                self.assertEqual((record[offset + 7], record[offset + 8]), (0, 0))

    def test_median_shift_all_orderings(self):
        config = (U8 * 1)()
        for values in itertools.permutations((10, 20, 30)):
            current = (U8 * 2)()
            history = (U8 * 4)()
            put16(current, 0, values[0])
            put16(history, 0, values[1])
            put16(history, 2, values[2])
            self.lib.open_cfw_touch_pipeline_1cc2_median_shift(
                config, current, history)
            self.assertEqual(get16(current, 0), 20)
            self.assertEqual((get16(history, 0), get16(history, 2)),
                             (values[0], values[1]))

    def test_update_counter_reset_guard_and_blend_paths(self):
        config = (U8 * 0x76)()
        nested = (U8 * 0x29)()
        nested_pointer = ctypes.cast(nested, U8P)
        nested_ref = ctypes.pointer(nested_pointer)
        unused = (U8 * 1)()
        record = (U8 * 10)()
        put16(config, 0x0C, 2)
        put16(config, 0x1A, 3)
        put16(config, 0x1C, 4)
        config[0x22] = 64

        put16(record, 0, 10)
        put16(record, 2, 20)
        record[7] = 1
        self.assertEqual(self.lib.open_cfw_touch_pipeline_1cee_update(
            config, record, unused, nested_ref), 0)
        self.assertEqual(record[7], 2)

        record[7] = 2
        self.lib.open_cfw_touch_pipeline_1cee_update(
            config, record, unused, nested_ref)
        self.assertEqual(get16(record, 2), 10)
        self.assertEqual((record[7], record[8]), (0, 0))

        put16(record, 0, 30)
        put16(record, 2, 20)
        record[8] = 0x80
        before = bytes(record)
        self.lib.open_cfw_touch_pipeline_1cee_update(
            config, record, unused, nested_ref)
        self.assertEqual(bytes(record), before[:7] + b"\x00" + before[8:])

        nested[0x28] = 1
        record[7] = 9
        expected = blend(30 << 8, (20 << 8) | 0x80, 64)
        self.lib.open_cfw_touch_pipeline_1cee_update(
            config, record, unused, nested_ref)
        self.assertEqual(get16(record, 2), (expected >> 8) & 0xFFFF)
        self.assertEqual(record[8], expected & 0xFF)
        self.assertEqual(record[7], 0)

    def test_blend_integer_and_fractional_paths(self):
        for fixed_point in (False, True):
            config = (U8 * 0x76)()
            current = (U8 * 2)()
            history = (U8 * 2)()
            fraction = (U8 * 1)(0x80)
            put16(config, 0x74, 0x0200 if fixed_point else 0)
            put32(config, 0x24, 64)
            put16(current, 0, 100)
            put16(history, 0, 20)
            self.lib.open_cfw_touch_pipeline_1d54_blend(
                config, current, history, fraction)
            if fixed_point:
                expected = blend(100 << 8, (20 << 8) | 0x80, 64)
                self.assertEqual(get16(current, 0), expected >> 8)
                self.assertEqual(fraction[0], expected & 0xFF)
            else:
                expected = blend(100, 20, 64) & 0xFFFF
                self.assertEqual(get16(current, 0), expected)
                self.assertEqual(fraction[0], 0x80)
            self.assertEqual(get16(history, 0), get16(current, 0))

    def test_filter_chain_flag_order_and_offsets(self):
        for bits in range(8):
            flags = ((bits & 1) << 4) | ((bits & 2) << 6) | ((bits & 4) << 8)
            config = (U8 * 0x76)()
            direct_current = (U8 * 2)()
            chain_current = (U8 * 2)()
            direct_history = (U8 * 12)()
            chain_history = (U8 * 12)()
            direct_fraction = (U8 * 1)(0x33)
            chain_fraction = (U8 * 1)(0x33)
            put16(config, 0x74, flags)
            put32(config, 0x24, 96)
            put16(direct_current, 0, 80)
            put16(chain_current, 0, 80)
            for offset, value in zip(range(0, 12, 2), (10, 90, 30, 40, 50, 60)):
                put16(direct_history, offset, value)
                put16(chain_history, offset, value)

            history_offset = 0
            if bits & 1:
                self.lib.open_cfw_touch_pipeline_1cc2_median_shift(
                    config, direct_current, pointer_at(direct_history, history_offset))
                history_offset += 4
            if bits & 2:
                self.lib.open_cfw_touch_pipeline_1d54_blend(
                    config, direct_current, pointer_at(direct_history, history_offset),
                    direct_fraction)
                history_offset += 2
            if bits & 4:
                self.lib.open_cfw_touch_record_1c6e_history_filter(
                    config, direct_current, pointer_at(direct_history, history_offset))

            self.lib.open_cfw_touch_pipeline_1da0_filter_chain(
                config, chain_current, chain_history, chain_fraction)
            self.assertEqual(bytes(chain_current), bytes(direct_current))
            self.assertEqual(bytes(chain_history), bytes(direct_history))
            self.assertEqual(bytes(chain_fraction), bytes(direct_fraction))

    def test_cortex_m0plus_compile_symbol_closure(self):
        clang = shutil.which("clang")
        nm = shutil.which("nm")
        if clang is None or nm is None:
            self.skipTest("clang/nm unavailable")
        objects = []
        for source in SOURCES:
            output = Path(self.temp.name) / (source.stem + ".o")
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
                "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            objects.append(output)
        defined = set()
        undefined = set()
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
