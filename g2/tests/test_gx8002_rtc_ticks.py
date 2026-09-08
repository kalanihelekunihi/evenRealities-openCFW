# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_rtc_ticks as v

class RtcTickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.start();v.set_tick()
        cls.start=v.decode((v.ROOT/'build/gx8002-board/rtc-start-tick-candidate.disassembly.txt').read_text())
        cls.setter=v.decode((v.ROOT/'build/gx8002-board/rtc-set-tick-candidate.disassembly.txt').read_text())

    def test_start_preserves_other_bits(self):
        for word in (0,0xffffffff,0x12345678):
            self.assertEqual(v.execute(self.start,0x102066a0,word,'start'),v.expected(word,'start'))

    def test_set_has_no_read(self):
        self.assertEqual(v.execute(self.setter,0x102066b0,0xffffffff,'set'),[('write',0xa0003008,0xffffffff)])

    def test_wrong_start_bit_changes_contract(self):
        code=self.start.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='ori')
        op,args,w=code[pc];code[pc]=(op,args[:-1]+'8',w)
        self.assertNotEqual(v.execute(code,0x102066a0,0,'start'),v.expected(0,'start'))

    def test_wrong_base_rejected(self):
        code=self.setter.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='lrw')
        op,args,w=code[pc];code[pc]=(op,args.replace('0xa0003000','0xa0004000'),w)
        with self.assertRaisesRegex(ValueError,'register address'):v.execute(code,0x102066b0,0,'set')

if __name__=='__main__':unittest.main()
