# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_spi_transfer_tx import Case,expected,REGS

class TXModelTests(unittest.TestCase):
    def test_little_endian_widths(self):
        for bits,words in ((8,[18,52,86,120]),(16,[0x3412,0x7856]),(32,[0x78563412])):
            trace,result=expected(Case(bits=bits))
            self.assertEqual(result,0)
            self.assertEqual([t[2] for t in trace if t[:2]==('write',REGS+96)],words)

    def test_full_fifo_then_progress(self):
        trace,_=expected(Case(levels=(16,0)))
        self.assertIn(('write',REGS+4,0xffffffff),trace)

    def test_delayed_ready_and_busy(self):
        trace,_=expected(Case(status=(0,1,4,1,0)))
        self.assertEqual([t[2] for t in trace if t[:2]==('read',REGS+40)],[0,1,4,1,0])

    def test_incomplete_fifo_does_not_pass(self):
        with self.assertRaisesRegex(ValueError,'exhausted'):
            expected(Case(levels=(16,)))

if __name__=='__main__': unittest.main()
