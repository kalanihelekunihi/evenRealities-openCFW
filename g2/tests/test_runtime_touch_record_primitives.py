# SPDX-License-Identifier: MIT
"""Host and CM0+ tests for call-free touch record transforms."""

import ctypes
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_record_primitives.c"
FIXTURE = ROOT / "tests/fixtures/touch_record_primitives_host.c"
U8P = ctypes.POINTER(ctypes.c_uint8)


def put16(buffer, offset, value):
    buffer[offset] = value & 0xFF
    buffer[offset + 1] = (value >> 8) & 0xFF


def get16(buffer, offset):
    return buffer[offset] | (buffer[offset + 1] << 8)


class TouchRecordPrimitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "libtouch_record_primitives.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH), str(SOURCE), str(FIXTURE),
            "-o", str(library),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_touch_record_1ab8_reset.argtypes = [U8P]
        cls.lib.touch_host_record_copy_gate.argtypes = [U8P, U8P, U8P, U8P, ctypes.c_int]
        cls.lib.open_cfw_touch_record_1b58_replicate2.argtypes = [U8P, U8P]
        cls.lib.open_cfw_touch_record_1b60_replicate3.argtypes = [U8P, U8P]
        cls.lib.open_cfw_touch_record_1c6e_history_filter.argtypes = [U8P, U8P, U8P]
        cls.lib.open_cfw_touch_record_1e88_mask3.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_touch_record_2620_threshold_delta.argtypes = [U8P, U8P]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_record_reset_preserves_only_established_fields(self):
        record = (ctypes.c_uint8 * 10)(*range(10))
        expected_first = get16(record, 0)
        self.lib.open_cfw_touch_record_1ab8_reset(record)
        self.assertEqual(get16(record, 2), expected_first)
        self.assertEqual(record[7], 0)
        self.assertEqual(record[8], 0)

    def test_copy_gate_all_partitions_and_optional_pointer(self):
        for setting in (0x0000, 0x0100, 0x0200, 0x0300, 0xFE00):
            config = (ctypes.c_uint8 * 0x76)()
            source = (ctypes.c_uint8 * 2)()
            destination = (ctypes.c_uint8 * 2)()
            gate = (ctypes.c_uint8 * 1)(0xA5)
            put16(config, 0x74, setting)
            put16(source, 0, 0xBEEF)
            self.lib.touch_host_record_copy_gate(
                config, source, destination, gate, 1)
            self.assertEqual(get16(destination, 0), 0xBEEF)
            self.assertEqual(gate[0], 0 if (setting & 0x300) == 0x200 else 0xA5)
            self.lib.touch_host_record_copy_gate(
                config, source, destination, gate, 0)

    def test_replicate_two_and_three(self):
        source = (ctypes.c_uint8 * 2)()
        destination = (ctypes.c_uint8 * 6)()
        put16(source, 0, 0xCAFE)
        self.lib.open_cfw_touch_record_1b58_replicate2(source, destination)
        self.assertEqual([get16(destination, offset) for offset in (0, 2)],
                         [0xCAFE, 0xCAFE])
        put16(source, 0, 0x1234)
        self.lib.open_cfw_touch_record_1b60_replicate3(source, destination)
        self.assertEqual([get16(destination, offset) for offset in (0, 2, 4)],
                         [0x1234, 0x1234, 0x1234])

    def test_history_filter_two_and_four_sample_paths(self):
        rng = random.Random(0x1C6E)
        for four_sample in (False, True):
            for _ in range(128):
                values = [rng.randrange(0x10000) for _ in range(4)]
                config = (ctypes.c_uint8 * 0x76)()
                current = (ctypes.c_uint8 * 2)()
                history = (ctypes.c_uint8 * 6)()
                put16(config, 0x74, 0x1000 if four_sample else 0)
                put16(current, 0, values[0])
                for offset, value in zip((0, 2, 4), values[1:]):
                    put16(history, offset, value)
                self.lib.open_cfw_touch_record_1c6e_history_filter(
                    config, current, history)
                if four_sample:
                    self.assertEqual(get16(current, 0), sum(values) >> 2)
                    self.assertEqual([get16(history, x) for x in (0, 2, 4)],
                                     [values[0], values[1], values[2]])
                else:
                    self.assertEqual(get16(current, 0),
                                     (values[0] + values[1]) >> 1)
                    self.assertEqual(get16(history, 0), values[0])

    def test_three_word_mask_transform(self):
        rng = random.Random(0x1E88)
        for flags in range(8):
            for _ in range(32):
                mask = rng.getrandbits(32)
                original = [rng.getrandbits(32) for _ in range(3)]
                words = (ctypes.c_uint32 * 3)(*original)
                self.lib.open_cfw_touch_record_1e88_mask3(mask, flags, words)
                expected = [
                    (original[i] & ~mask) | (mask if flags & (4 >> i) else 0)
                    for i in range(3)
                ]
                self.assertEqual(list(words), [value & 0xFFFFFFFF for value in expected])

    def test_threshold_delta(self):
        for value0, value1, threshold in (
                (100, 20, 10), (30, 20, 10), (29, 20, 10),
                (0xFFFF, 0xFFFE, 0xFFFF)):
            config = (ctypes.c_uint8 * 0x1C)()
            record = (ctypes.c_uint8 * 6)()
            put16(config, 0x1A, threshold)
            put16(record, 0, value0)
            put16(record, 2, value1)
            put16(record, 4, 0xA5A5)
            self.lib.open_cfw_touch_record_2620_threshold_delta(config, record)
            expected = (value0 - value1) & 0xFFFF if value0 > value1 + threshold else 0
            self.assertEqual(get16(record, 4), expected)

    def test_cortex_m0plus_compile(self):
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch_record_primitives.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
