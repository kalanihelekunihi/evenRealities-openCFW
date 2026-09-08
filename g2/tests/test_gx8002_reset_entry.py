# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_reset_entry import ROOT,decode,execute
class ResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/reset-entry.disassembly.txt').read_text())
    def test_bad_stack_rejected(self):
        code=self.code.copy();code[0x10023510]=('lrw','r3, 0x20000000',2)
        with self.assertRaisesRegex(ValueError,'reset stack'):execute(code,0,0)
    def test_wrong_control_register_rejected(self):
        code=self.code.copy();code[0x10023506]=('mfcr','r1, cr<30, 0>',4)
        with self.assertRaisesRegex(ValueError,'control source'):execute(code,0,0)
    def test_unknown_main_rejected(self):
        code=self.code.copy();code[0x10023518]=('bsr','0x10020000',4)
        with self.assertRaisesRegex(ValueError,'unknown reset call'):execute(code,0,0)
    def test_wrong_exit_rejected(self):
        code=self.code.copy();code[0x1002351c]=('br','0x10023500',2)
        with self.assertRaisesRegex(ValueError,'returned-main loop'):execute(code,0,0)
if __name__=='__main__':unittest.main()
