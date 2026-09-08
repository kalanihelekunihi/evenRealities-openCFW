# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_main import ROOT,decode,execute
class MainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/main-candidate.disassembly.txt').read_text())
    def test_missing_frame(self):
        code=self.code.copy();code[0x10026314]=('bsr','0x102078a4',4)
        with self.assertRaisesRegex(ValueError,'call frame'):execute(code,0x10026314,0,[0])
    def test_wrong_mode(self):
        code=self.code.copy();code[0x1002631a]=('movi','r0, 0',2)
        with self.assertRaisesRegex(ValueError,'wrong initial mode'):execute(code,0x10026314,0,[0])
    def test_unknown_helper(self):
        code=self.code.copy();code[0x10026316]=('bsr','0x10020000',4)
        with self.assertRaisesRegex(ValueError,'unknown main helper'):execute(code,0x10026314,0,[0])
    def test_missing_tick(self):
        with self.assertRaisesRegex(ValueError,'missing tick'):execute(self.code,0x10026314,0,[1])
    def test_unused_tick(self):
        with self.assertRaisesRegex(ValueError,'unused tick'):execute(self.code,0x10026314,0,[0,1])
    def test_wrong_pop(self):
        code=self.code.copy();code[0x10026334]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):execute(code,0x10026314,0,[0])
if __name__=='__main__':unittest.main()
