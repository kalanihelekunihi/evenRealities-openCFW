# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_read import execute
class OtpReadTargetTests(unittest.TestCase):
    def run_code(self,code,events=None):return execute(code,0,0,0,0,1,events or [])
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'call frame'):
            self.run_code({0:('bsr','0x1002375c',4)})
    def test_missing_local_space(self):
        with self.assertRaisesRegex(ValueError,'call frame'):
            self.run_code({0:('push','r4-r11, r15, r16-r17',4),4:('bsr','0x1002375c',4)})
    def test_unknown_helper(self):
        with self.assertRaisesRegex(ValueError,'unknown helper'):
            self.run_code({0:('push','r4-r11, r15, r16-r17',4),4:('subi','r14, r14, 4',2),6:('bsr','0x10023e14',4)})
    def test_extra_byte(self):
        with self.assertRaisesRegex(ValueError,'extra effect'):
            self.run_code({0:('ld.b','r0, (r0, 0x0)',2)})
    def test_missing_effect(self):
        with self.assertRaisesRegex(ValueError,'return ABI/effects'):
            self.run_code({0:('push','r4-r11, r15, r16-r17',4),4:('pop','r4-r11, r15, r16-r17',4)},[['call',0x1002375c,[]]])
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown write instruction'):
            self.run_code({0:('invalid','',2)})
if __name__=='__main__':unittest.main()
