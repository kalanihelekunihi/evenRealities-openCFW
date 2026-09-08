# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_uid_read import execute
class UidTargetTests(unittest.TestCase):
    def run_code(self,code,events=None):return execute(code,0,0,0,1,0x20029000,events or [])
    def test_call_requires_frame(self):
        with self.assertRaisesRegex(ValueError,'call frame'):
            self.run_code({0:('bsr','0x1002364c',4)})
    def test_wrong_saved_set(self):
        with self.assertRaisesRegex(ValueError,'frame'):
            self.run_code({0:('push','r4-r6, r15',2)})
    def test_unknown_helper(self):
        with self.assertRaisesRegex(ValueError,'unknown helper'):
            self.run_code({0:('push','r4-r5, r15',2),2:('bsr','0x1002375c',4)})
    def test_extra_effect(self):
        with self.assertRaisesRegex(ValueError,'extra effect'):
            self.run_code({0:('ld.b','r0, (r0, 0x0)',2)})
    def test_missing_count_store(self):
        with self.assertRaisesRegex(ValueError,'return ABI/effects'):
            self.run_code({0:('push','r4-r5, r15',2),2:('pop','r4-r5, r15',2)},[['write',0x20029000,0]])
if __name__=='__main__':unittest.main()
