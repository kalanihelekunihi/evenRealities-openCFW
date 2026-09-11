# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_clock_dto_slice as v

class DtoSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.link()
        cls.code = v.decode((v.ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text())

    def run_slice(self, present, word, frequency, code=None):
        return v.execute(self.code if code is None else code,
                         0x10025390, 0x100252ac, present, word, frequency)

    def test_absent_descriptor_does_not_read_mmio(self):
        self.assertEqual(self.run_slice(False, v.MASK, 98304000),
                         ([(v.PARAM+12, 4, 0)], 98304000))

    def test_bypass_and_full_width_product(self):
        for word in (0, 1, 0x1ffffff, 0x8000000, v.MASK):
            self.assertEqual(self.run_slice(True, word, v.MASK),
                             v.expected(True, word, v.MASK))

    def test_wrong_numerator_mask_changes_result(self):
        code = self.code.copy()
        op, args, width = code[0x100253a8]
        code[0x100253a8] = (op, args.replace('24', '23'), width)
        self.assertNotEqual(self.run_slice(True, 0x1ffffff, v.MASK, code),
                            v.expected(True, 0x1ffffff, v.MASK))

    def test_wrong_descriptor_offset_rejected(self):
        code = self.code.copy()
        op, args, width = code[0x10025390]
        code[0x10025390] = (op, args.replace('0xc', '0x8'), width)
        with self.assertRaisesRegex(ValueError, 'read address'):
            self.run_slice(True, 1, 98304000, code)

if __name__ == '__main__':
    unittest.main()
