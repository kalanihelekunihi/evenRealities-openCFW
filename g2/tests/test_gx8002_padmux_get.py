# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_padmux_get as v

class PadmuxGetterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build();cls.old,cls.new=v.programs()

    def mutate(self,op,args,replacement):
        code=self.new.copy()
        pc=next(pc for pc,(o,a,w) in code.items() if o==op and a==args)
        _,_,width=code[pc];code[pc]=(op,replacement,width)
        return code

    def test_pin_32_and_invalid_boundaries(self):
        for pin in (32,33,0x80000000,0xffffffff):
            self.assertEqual(v.execute(self.new,v.ADDRESS,pin,0xabcdef01),v.expected(pin,0xabcdef01))

    def test_wrong_word_address_rejected(self):
        code=self.mutate('lrw','r2, 0xa0010090','r2, 0xa0010094')
        with self.assertRaisesRegex(ValueError,'read address'): v.execute(code,v.ADDRESS,8,0)

    def test_wrong_nibble_mask_detected(self):
        code=self.mutate('andi','r0, r3, 15','r0, r3, 31')
        self.assertNotEqual(v.execute(code,v.ADDRESS,0,0xffffffff),v.expected(0,0xffffffff))

    def test_wrong_upper_bound_rejected(self):
        code=self.mutate('cmphsi','r0, 33','r0, 34')
        with self.assertRaisesRegex(ValueError,'read address'): v.execute(code,v.ADDRESS,33,0)

if __name__=='__main__': unittest.main()
