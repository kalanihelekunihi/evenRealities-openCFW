# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_flash_interrupt import execute
class FlashInterruptTests(unittest.TestCase):
    def test_extra_read(self):
        with self.assertRaisesRegex(ValueError,'unexpected read'):
            execute({0:('ld.w','r0, (r0, 0x0)',2)},0,[])
    def test_missing_read(self):
        with self.assertRaisesRegex(ValueError,'return mismatch'):
            execute({0:('rts','',2)},0,[[0xa2000030,0]])
    def test_preserved_register(self):
        with self.assertRaisesRegex(ValueError,'return mismatch'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,[])
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown interrupt instruction'):
            execute({0:('invalid','',2)},0,[])
if __name__=='__main__':unittest.main()
