# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_full import execute,decode,ROOT

class ResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/flash.disassembly.txt').read_text())
    def run_code(self,code=None,mapping=None):
        return execute(self.code if code is None else code,0x100245f0,0,0,0,0,0,0,
                       readonly_configuration={0x100246c0:0} if mapping is None else mapping)
    def test_missing_constant_rejected(self):
        with self.assertRaisesRegex(ValueError,'constant configuration'):self.run_code(mapping={})
    def test_nonzero_constant_rejected(self):
        with self.assertRaisesRegex(ValueError,'constant configuration'):self.run_code(mapping={0x100246c0:1})
    def test_wrong_constant_pointer_rejected(self):
        code=self.code.copy();code[0x100245f4]=('lrw','r1, 0x100246bc',2)
        with self.assertRaisesRegex(ValueError,'constant configuration'):self.run_code(code)
    def test_missing_frame_rejected(self):
        with self.assertRaisesRegex(ValueError,'call frame'):
            execute({0:('bsr','0x10025d74',4)},0,0,0,0,0,0,0)
    def test_oversized_frame_rejected(self):
        code=self.code.copy();code[0x100245f2]=('subi','r14, r14, 24',2)
        with self.assertRaisesRegex(ValueError,'call frame'):self.run_code(code)
    def test_wrong_operation_rejected(self):
        code=self.code.copy();code[0x100245f6]=('movi','r0, 8',2)
        with self.assertRaisesRegex(ValueError,'configuration operation'):self.run_code(code)
    def test_unknown_helper_rejected(self):
        code=self.code.copy();code[0x100245f8]=('bsr','0x10020000',4)
        with self.assertRaisesRegex(ValueError,'unknown setup call'):self.run_code(code)
if __name__=='__main__':unittest.main()
