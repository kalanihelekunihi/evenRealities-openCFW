# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_tws_shutdown import ROOT,decode,execute,expected
class TwsLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/tws-shutdown-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,pc=0x1020864c,result=0xffffffff):return execute(self.code if code is None else code,pc,0,0xdeadbeef,result)
    def test_shutdown_order(self):self.assertEqual(self.run_case()[0],expected('done',0)[0])
    def test_buffer_return(self):
        for value in (0,1,0x80000000,0xffffffff):self.assertEqual(self.run_case(pc=0x10208644,result=value),expected('buffer',value))
    def test_clear_extent(self):
        c=self.code.copy();c[0x1020864e]=('movi','r2, 16',2)
        self.assertNotEqual(self.run_case(c)[0],expected('done',0)[0])
    def test_clear_address(self):
        c=self.code.copy();c[0x10208652]=('lrw','r0, 0x2002e700',2)
        self.assertNotEqual(self.run_case(c)[0],expected('done',0)[0])
    def test_call_order(self):
        c=self.code.copy();c[0x10208658]=('bsr','0x102073f8',4);c[0x1020865c]=('bsr','0x10206dac',4)
        self.assertNotEqual(self.run_case(c)[0],expected('done',0)[0])
    def test_wrong_buffer_helper(self):
        c=self.code.copy();c[0x10208646]=('bsr','0x10206dac',4)
        self.assertNotEqual(self.run_case(c,pc=0x10208644),expected('buffer',0xffffffff))
    def test_bad_return_frame(self):
        c=self.code.copy();c[0x10208666]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
