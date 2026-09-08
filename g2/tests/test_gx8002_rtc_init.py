# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_rtc_init as v

class RtcInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build();cls.code=v.decode((v.ROOT/'build/gx8002-board/rtc-init-candidate.disassembly.txt').read_text())

    def test_prescaler_boundary(self):
        for frequency in (65535,65536,0xffffffff):
            self.assertEqual(v.execute(self.code,v.ADDRESS,frequency,0),v.expected(frequency,0))

    def test_error_keeps_prior_enable_and_control_write(self):
        trace=v.execute(self.code,v.ADDRESS,65536,2)
        self.assertEqual(trace,[('gate',0,1),('read',0xa000300c,2),('write',0xa000300c,18),('frequency',0),('printf',0x1020ad04)])

    def test_zero_frequency_still_installs_irq(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,0,0)[-2:],[('irq',4,0x10206680,0),('start',)])

    def test_failed_frequency_skips_start_hook(self):
        def fail():raise AssertionError('Unexpected start')
        self.assertEqual(v.execute(self.code,v.ADDRESS,65536,0,start_hook=fail),v.expected(65536,0))

    def test_success_invokes_start_hook_once(self):
        seen=[]
        v.execute(self.code,v.ADDRESS,32768,0,start_hook=lambda:seen.append('start'))
        self.assertEqual(seen,['start'])

    def test_wrong_helper_target_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='bsr')
        op,args,w=code[pc];code[pc]=(op,'0x10025084',w)
        with self.assertRaisesRegex(ValueError,'helper target'):v.execute(code,v.ADDRESS,1,0)

if __name__=='__main__':unittest.main()
