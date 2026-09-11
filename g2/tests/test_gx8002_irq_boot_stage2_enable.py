# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_irq_boot_stage2_enable as v


class IrqBootStage2EnableInterpreterTests(unittest.TestCase):
    def test_rejects_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError, 'unsupported instruction'):
            v.execute({0: ('bkpt', '', 2)}, 0, 0)

    def test_rejects_return_without_a_vic_write(self):
        with self.assertRaisesRegex(ValueError, 'returned without a VIC write'):
            v.execute({0: ('rts', '', 2)}, 0, 0)

    def test_two_and_three_operand_lsl_agree(self):
        two = {0: ('movi', 'r1, 1', 2), 2: ('lsl', 'r1, r0', 2),
               4: ('lrw', 'r2, 0xe000e100', 2), 6: ('str.w', 'r1, (r2, r0 << 2)', 4)}
        three = {0: ('movi', 'r1, 1', 2), 2: ('lsl', 'r1, r1, r0', 2),
                 4: ('lrw', 'r2, 0xe000e100', 2), 6: ('str.w', 'r1, (r2, r0 << 2)', 4)}
        for irqn in (0, 3, 31):
            self.assertEqual(v.execute(two, 0, irqn), v.execute(three, 0, irqn))

    def test_zext_extracts_index_bits(self):
        code = {0: ('zext', 'r1, r0, 6, 5', 4), 4: ('movi', 'r2, 1', 2),
                6: ('lrw', 'r3, 0xe000e100', 2), 8: ('str.w', 'r2, (r3, r1 << 2)', 4)}
        self.assertEqual(v.execute(code, 0, 0b1100000)[0], v.VIC_BASE + 4 * 3)

    def test_end_to_end_matches_the_second_stock_occurrence(self):
        report = v.verify()
        row = report['functions'][0]
        self.assertEqual(row['symbol'], v.SYMBOL)
        self.assertEqual(row['ownership_kind'], 'compiled_c')
        occurrence = row['stock_occurrences'][0]
        self.assertEqual(occurrence['package_offset'], v.PACKAGE_OFFSET)
        self.assertEqual(occurrence['bytes'], v.ENVELOPE_BYTES)
        self.assertEqual(occurrence['region'], 'boot_stage2')
        self.assertGreater(report['decoded_cases'], 200)
        self.assertTrue(report['source_admitted'])
        self.assertFalse(report['hardware_qualified'])


if __name__ == '__main__':
    unittest.main()
