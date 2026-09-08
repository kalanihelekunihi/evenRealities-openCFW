# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_status import execute
class OtpStatusTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,0,0,0x85,0,0)
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'frame mismatch'):
            self.run_code({0:('bsr','0x1002375c',4)})
    def test_wrong_helper(self):
        with self.assertRaisesRegex(ValueError,'unexpected helper'):
            self.run_code({0:('push','r4-r6, r15',2),2:('bsr','0x10023770',4)})
    def test_unexpected_output(self):
        with self.assertRaisesRegex(ValueError,'unexpected output'):
            self.run_code({0:('st.b','r0, (r0, 0x0)',2)})
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown OTP instruction'):
            self.run_code({0:('invalid','',2)})
if __name__=='__main__':unittest.main()
