# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_block_wrapper import execute
class BlockWrapperTests(unittest.TestCase):
    def run_code(self,code):
        return execute(code,0,0,0,1,0x20028000,0x20028004,(-1,))
    def test_wrong_helper(self):
        with self.assertRaisesRegex(ValueError,'wrong helper'):
            self.run_code({0:('bsr','0x100238a6',4)})
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'frame mismatch'):
            self.run_code({0:('bsr','0x100238a4',4)})
    def test_wrong_arguments(self):
        with self.assertRaisesRegex(ValueError,'call arguments mismatch'):
            self.run_code({0:('push','r4-r6, r15',2),2:('subi','r14, r14, 4',2),4:('bsr','0x100238a4',4)})
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown wrapper instruction'):
            self.run_code({0:('invalid','',2)})
if __name__=='__main__':unittest.main()
