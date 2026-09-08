# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_dw_spi_irq as v

class IRQTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.stock,cls.source = v.programs()

    def test_all_branch_combinations(self):
        for status in (0,2,8,10,0xffffffff):
            self.assertEqual(v.execute(self.source,v.ADDRESS,status,123,456,0),v.expected(status,123,456))

    def test_controller_relative_substitution_is_rejected(self):
        code = self.source.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='movi' and args=='r2, 0')
        op,args,width = code[pc]
        code[pc] = (op,'r2, 0xa0002000',width)
        with self.assertRaisesRegex(ValueError,'Unexpected IRQ read'):
            v.execute(code,v.ADDRESS,2,123,456,0)

    def test_read_value_does_not_replace_snapshot(self):
        self.assertEqual(v.execute(self.source,v.ADDRESS,10,0,0,0),v.expected(10,0,0))
        self.assertEqual(v.execute(self.source,v.ADDRESS,2,8,0,0),v.expected(2,8,0))

    def test_wrong_mask_is_detected(self):
        code = self.source.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='andi' and args.endswith(', 8'))
        op,args,width = code[pc]
        code[pc] = (op,args[:-1]+'4',width)
        self.assertNotEqual(v.execute(code,v.ADDRESS,8,0,1,0),v.expected(8,0,1))

    def test_preserved_register_corruption_is_rejected(self):
        code = self.source.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='movi' and args=='r0, 0')
        op,args,width = code[pc]
        code[pc] = (op,'r4, 0',width)
        with self.assertRaisesRegex(ValueError,'leaf ABI'):
            v.execute(code,v.ADDRESS,0,0,0,0)

if __name__ == '__main__':
    unittest.main()
