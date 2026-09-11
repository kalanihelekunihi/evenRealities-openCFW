# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_clock_frequency_return as v

class ReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build_probe()
        cls.code=v.decode((v.ROOT/'build/gx8002-clock-frequency-size-probe/analysis.disassembly.txt').read_text())
    def run_return(self,divider,code=None):
        return v.execute(self.code if code is None else code,0x100252a6,0,98304000,divider)
    def test_zero_and_nonzero_divider(self):
        self.assertEqual(self.run_return(0)[1],98304000)
        self.assertEqual(self.run_return(3)[1],32768000)
    def test_wrong_helper_rejected(self):
        code=self.code.copy();op,args,width=code[0x100252a8]
        code[0x100252a8]=(op,'0x10024aec',width)
        with self.assertRaisesRegex(ValueError,'divider target'):self.run_return(2,code)
    def test_wrong_stack_adjustment_rejected(self):
        code=self.code.copy();op,args,width=code[0x10025248]
        code[0x10025248]=(op,'r14, r14, 20',width)
        with self.assertRaisesRegex(ValueError,'frame'):self.run_return(2,code)

if __name__=='__main__':unittest.main()
