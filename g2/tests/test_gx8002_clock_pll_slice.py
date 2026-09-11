# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_clock_pll_slice as v

class PllSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.link();cls.code=v.decode((v.ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text())
    def run_slice(self,words,code=None):
        return v.execute(self.code if code is None else code,0x100252f2,(0x10025390,0x10025246),words)
    def test_nominal_and_overflow(self):
        for words in ((0,59,0,0,0),(63,2047,0,0,48)):
            self.assertEqual(self.run_slice(words)[1],v.frequency(*words))
    def test_read_sequence(self):
        reads,result=self.run_slice((0,59,0,0,0))
        self.assertEqual([a for a,w in reads],[0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030])
    def test_wrong_register_offset_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if pc>=0x100252f2 and op=='ld.w' and '0x1c' in a)
        op,args,w=code[pc];code[pc]=(op,args.replace('0x1c','0x18'),w)
        with self.assertRaisesRegex(ValueError,'read address'):self.run_slice((0,59,0,0,0),code)
    def test_wrong_input_mask_changes_result(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if pc>=0x100252f2 and op=='andi' and a.endswith('63'))
        op,args,w=code[pc];code[pc]=(op,args[:-2]+'31',w)
        words=(63,2047,0,0,48)
        self.assertNotEqual(self.run_slice(words,code)[1],v.frequency(*words))
if __name__=='__main__':unittest.main()
