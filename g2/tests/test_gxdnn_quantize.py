# SPDX-License-Identifier: MIT
"""Tests for the gxDNN half-precision quantizer used by the command emitter."""
import math
import random
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from gxdnn_quantize import quantize_half, dequantize_half, quantize_tensor, dequantize_tensor


class HalfQuantizeTests(unittest.TestCase):
    KNOWN_VALUES = [
        (0.0, 0x0000), (-0.0, 0x8000), (1.0, 0x3C00), (-1.0, 0xBC00),
        (0.5, 0x3800), (2.0, 0x4000), (-2.0, 0xC000), (1.5, 0x3E00),
    ]

    def test_known_ieee754_binary16_values(self):
        for value, bits in self.KNOWN_VALUES:
            self.assertEqual(quantize_half(value), bits)
            if value == 0.0:
                self.assertEqual(dequantize_half(bits), 0.0)
            else:
                self.assertEqual(dequantize_half(bits), value)

    def test_round_trip_within_half_precision(self):
        rng = random.Random(6)
        for _ in range(5000):
            value = rng.uniform(-1000.0, 1000.0)
            bits = quantize_half(value)
            self.assertTrue(0 <= bits < 0x10000)
            recovered = dequantize_half(bits)
            # Half precision has ~3 significant decimal digits.
            if value != 0:
                self.assertLess(abs(recovered - value) / max(abs(value), 1e-6), 0.02)

    def test_matches_python_struct_e_directly(self):
        rng = random.Random(7)
        for _ in range(5000):
            value = rng.uniform(-65000.0, 65000.0)
            expected = struct.unpack('<H', struct.pack('<e', value))[0]
            self.assertEqual(quantize_half(value), expected)

    def test_dequantize_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            dequantize_half(-1)
        with self.assertRaises(ValueError):
            dequantize_half(0x10000)

    def test_tensor_round_trip(self):
        values = [0.0, 1.0, -1.0, 0.5, 3.25, -12.75, 100.0]
        data = quantize_tensor(values)
        self.assertEqual(len(data), 2 * len(values))
        recovered = dequantize_tensor(data)
        for expected, actual in zip(values, recovered):
            self.assertEqual(expected, actual)

    def test_tensor_rejects_odd_length(self):
        with self.assertRaises(ValueError):
            dequantize_tensor(b'\x00\x00\x00')


if __name__ == '__main__':
    unittest.main()
