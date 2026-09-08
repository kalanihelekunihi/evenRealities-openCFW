# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_gpio_output as v


class GPIOOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v.verify()
        cls.old, cls.new = v.programs()

    def test_cases(self):
        self.assertEqual(self.report['cases'], 8040)

    def test_direction_order(self):
        words = {0xa0001000: 0, 0xa0001004: 0, 0xa0001008: 0xffffffff}
        trace, final, result = v.execute(self.new, 0x10205f24, 31, 1, words, 0)
        self.assertEqual([x[:2] for x in trace], [('read', 0xa0001008), ('write', 0xa0001008), ('read', 0xa0001000), ('write', 0xa0001000)])
        self.assertEqual(final[0xa0001000], 0x80000000)

    def test_invalid_direction_no_mmio(self):
        self.assertEqual(v.execute(self.new, 0x10205f24, 0, 0xffffffff, {}, 0), ([], {}, 0))

    def test_nonzero_level_and_wrapped_pin(self):
        words = {0xa0001004: 0}
        self.assertEqual(v.execute(self.new, 0x10205f88, 63, 2, words, 0)[1][0xa0001004], 0x80000000)

    def test_wrong_port_mask_detected(self):
        code = self.new.copy()
        pc = 0x10205f26
        op, args, width = code[pc]
        code[pc] = (op, 'r2, r0, 15', width)
        words = {0xa0001000: 0, 0xa0001008: 0xffffffff}
        self.assertNotEqual(v.execute(code, 0x10205f24, 31, 1, words, 0), v.expected('direction', 31, 1, words))

    def test_abi_corruption_rejected(self):
        code = self.new.copy()
        code[0x10205fa2] = ('movi', 'r4, 0', 2)
        with self.assertRaisesRegex(ValueError, 'ABI'):
            v.execute(code, 0x10205f88, 1, 1, {0xa0001004: 0}, 0)


if __name__ == '__main__':
    unittest.main()
