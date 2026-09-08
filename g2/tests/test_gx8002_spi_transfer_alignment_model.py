# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_spi_transfer_alignment import Case,expected,TRANSFER,STATE,REGS

class AlignmentModelTests(unittest.TestCase):
    def test_length_failure_shuts_down(self):
        trace,result=expected(Case())
        self.assertEqual(result,0xffffffea)
        self.assertEqual(trace[-4:], [('write',0xa030008c,3),('clock',14,0),('write',STATE+16,0),('write',STATE+20,0)])

    def test_receive_buffer_alignment(self):
        trace,_=expected(Case(bits=32,length=4,buffer=0x20030001,transmit=False))
        self.assertIn(('read',TRANSFER+4,0x20030001),trace)
        self.assertIn(('write',REGS,0x8000081f),trace)

    def test_divider_is_truncated_then_clamped(self):
        trace,_=expected(Case(divider=0x10001))
        self.assertIn(('write',REGS+20,2),trace)

    def test_aligned_case_requires_next_model(self):
        with self.assertRaisesRegex(ValueError,'FIFO'):
            expected(Case(length=4))

if __name__=='__main__': unittest.main()
