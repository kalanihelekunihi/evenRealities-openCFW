# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_erase import execute
class OtpEraseTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,0,0x85,0,4096,4096,0)
    def test_wrong_helper(self):
        with self.assertRaisesRegex(ValueError,'helper order'):
            self.run_code({0:('bsr','0x10023770',4)})
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'frame mismatch'):
            self.run_code({0:('bsr','0x1002375c',4)})
    def test_missing_command(self):
        with self.assertRaisesRegex(ValueError,'missing command store'):
            self.run_code({0:('push','r4-r7, r15',2),2:('bsr','0x1002375c',4)})
    def test_premature_reload(self):
        with self.assertRaisesRegex(ValueError,'command reload'):
            self.run_code({0:('lrw','r4, 0x200264e4',2),2:('ld.b','r0, (r4, 0x10)',2)})
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown erase instruction'):
            self.run_code({0:('invalid','',2)})
if __name__=='__main__':unittest.main()
