# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_idle import execute,ROOT,decode
class IdleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/idle-candidate.disassembly.txt').read_text())
    def run_init(self,code):return execute(code,0x10208634,0,'init',0xffff,0xffffffff,0x80000000)
    def test_init_ignores_printf_return(self):self.assertEqual(self.run_init(self.code)['result'],0)
    def test_wrong_helper(self):
        c=self.code.copy();c[0x10208638]=('bsr','0x10206c28',4)
        with self.assertRaisesRegex(ValueError,'helper'):self.run_init(c)
    def test_wrong_message(self):
        c=self.code.copy();c[0x10208636]=('lrw','r0, 0x1020b1d8',2)
        with self.assertRaisesRegex(ValueError,'message'):self.run_init(c)
    def test_wrong_return(self):
        c=self.code.copy();c[0x1020863c]=('movi','r0, 1',2)
        self.assertNotEqual(self.run_init(c)['result'],0)
    def test_unrestored_frame(self):
        c=self.code.copy();c[0x1020863e]=('rts','',2)
        with self.assertRaisesRegex(ValueError,'outstanding frame'):self.run_init(c)
    def test_original_empty_tick(self):
        self.assertEqual(execute(self.code,0x1020861c,0,'tick',42,0,0),{'trace':[],'result':None})
if __name__=='__main__':unittest.main()
