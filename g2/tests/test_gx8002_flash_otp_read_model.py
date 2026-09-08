# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from model_gx8002_flash_otp_read import expected,MASK
class OtpReadModelTests(unittest.TestCase):
    def test_zero_short_circuit(self):
        result,trace=expected(0,0,0,512,4096,4096,0,0x85)
        self.assertEqual(result,MASK);self.assertEqual(len(trace),3)
    def test_final_encode_and_width_reload(self):
        result,trace=expected(0,0xfffffffe,33,512,4096,4096,0,0x85)
        self.assertEqual(result,33)
        self.assertEqual([e[2] for e in trace if e[:2]==['read',0x200264ec]],[4,3])
        encodes=[e[2][1] for e in trace if e[:2]==['call',0x10023b8c]]
        self.assertEqual(encodes,[4096,4128,4129])
        self.assertEqual(trace[-2],['call',0x10023b8c,[0x200264ec,4129,0x200264f4]])
        self.assertEqual(len([e for e in trace if e[0]=='byte-write']),33)
    def test_large_signed_chunk_not_silently_truncated(self):
        with self.assertRaisesRegex(ValueError,'large signed chunk'):
            expected(1,0,0xffffffff,0,4096,4096,0,0x85)
if __name__=='__main__':unittest.main()
