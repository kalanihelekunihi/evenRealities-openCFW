# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_transmit import execute,oracle
class OtpTransmitTests(unittest.TestCase):
    def test_zero_still_configures_and_cleans_up(self):
        events=oracle(0,0,0,0)
        self.assertIn(['write',0xa2000004,0xffffffff],events)
        self.assertEqual([e[1] for e in events if e[0]=='call'],[0x1002364c,0x10023670,0x1002375c])
        self.assertEqual([e[2] for e in events if e[:2]==['write',0xa2000010]],[0,1])
    def test_prefix_payload_order(self):
        events=oracle(2,0xfffffffe,3,0)
        self.assertEqual([e[1] for e in events if e[0]=='byte-read'],[0x200264f4,0x200264f5,0xfffffffe,0xffffffff,0])
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'frame mismatch'):
            execute({0:('bsr','0x1002364c',4)},0,0,0,0,[],0)
    def test_missing_effect(self):
        with self.assertRaisesRegex(ValueError,'return state mismatch'):
            execute({0:('rts','',2)},0,0,0,0,[['call',0x1002364c,0]],0)
    def test_unexpected_effect(self):
        with self.assertRaisesRegex(ValueError,'unexpected extra effect'):
            execute({0:('ld.b','r0, (r0, 0x0)',2)},0,0,0,0,[],0)
    def test_bad_saved_register(self):
        with self.assertRaisesRegex(ValueError,'return state mismatch'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,0,0,0,[],0)
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unknown read instruction'):
            execute({0:('invalid','',2)},0,0,0,0,[],0)
if __name__=='__main__':unittest.main()
