# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_kws_reset import ROOT,decode,execute
class ResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/kws-reset-candidate.disassembly.txt').read_text());cls.fill=decode((ROOT/'build/gx8002-board/memset-candidate.disassembly.txt').read_text())
    def run_case(self,code,entry=0x10208978):return execute(code,entry,0,self.fill,0x102099cc,0xffffffff)
    def test_nested_clear_extent(self):
        got=self.run_case(self.code);self.assertEqual(got['peak_frame_bytes'],8)
        writes=[e for e in got['trace'] if e[0]=='store'];self.assertEqual(len(writes),41)
        self.assertEqual(writes[0],['store',0x2002e7a8,4,0]);self.assertEqual(writes[-1],['store',0x2002e848,4,0])
    def test_wrong_clear_size(self):
        c=self.code.copy();c[0x10208966]=('movi','r2, 160',2)
        with self.assertRaisesRegex(ValueError,'extent'):self.run_case(c)
    def test_wrong_fill_byte(self):
        c=self.code.copy();c[0x10208968]=('movi','r1, 1',2)
        with self.assertRaisesRegex(ValueError,'extent'):self.run_case(c)
    def test_wrong_nested_target(self):
        c=self.code.copy();c[0x1020897a]=('bsr','0x10208968',4)
        with self.assertRaisesRegex(ValueError,'unknown reset helper'):self.run_case(c)
    def test_wrong_return_frame(self):
        c=self.code.copy();c[0x10208970]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
