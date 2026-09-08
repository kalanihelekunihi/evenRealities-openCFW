# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_board_initialize import execute,decode,ROOT
class BoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/board.disassembly.txt').read_text())
    def test_missing_frame(self):
        code=self.code.copy();code[0x10025cbc]=('bsr','0x10024940',4)
        with self.assertRaisesRegex(ValueError,'call frame'):execute(code,0)
    def test_unknown_helper(self):
        code=self.code.copy();code[0x10025cbe]=('bsr','0x10020000',4)
        with self.assertRaisesRegex(ValueError,'unknown board helper'):execute(code,0)
    def test_wrong_return_frame(self):
        code=self.code.copy();code[0x10025cce]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):execute(code,0)
    def test_undefined_condition(self):
        code=self.code.copy();code[0x10025cc2]=('bf','0x10025cca',2)
        with self.assertRaisesRegex(ValueError,'undefined condition'):execute(code,0)
    def test_boundary_dispatch(self):
        self.assertNotIn(['call',0x100245f0],execute(self.code,1))
        self.assertIn(['call',0x100245f0],execute(self.code,2))
        self.assertIn(['call',0x100245f0],execute(self.code,0xffffffff))
if __name__=='__main__':unittest.main()
