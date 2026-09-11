# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_clock_pll_frequency import frequency,quantize_input
class PllFrequencyModelTests(unittest.TestCase):
    def test_ordered_band_boundaries(self):
        for value,want in ((15999,None),(16000,32000),(47999,32000),(48000,None),(153599,None),(153600,2048000),(511999,2048000),(512000,1024000),(1535999,1024000),(1536000,2048000),(3071999,2048000),(3072000,None)):
            self.assertEqual(quantize_input(value),want)
    def test_nominal_feedback(self):
        self.assertEqual(frequency(0,59,0,0,0),30720000)
    def test_subband_and_output_division(self):
        for band,feedback in ((0,59),(1,71),(2,83),(3,95)):
            self.assertEqual(frequency(0,feedback,0,7,band<<4),1024000*(feedback+1)//16)
    def test_unsigned_multiply_wrap(self):
        self.assertEqual(frequency(63,2047,0,0,3<<4),16384000)
    def test_zero_feedback_divisor_rejected(self):
        with self.assertRaisesRegex(ValueError,'zero feedback'):frequency(0,0xffffffff,0,0,0)
if __name__=='__main__':unittest.main()
