# SPDX-License-Identifier: MIT
import unittest
from dataclasses import replace
from tools.model_gx8002_spi_transfer_message import Case,expected,TXCase,RXCase,STATE,MESSAGE,TRANSFER
from tools.model_gx8002_spi_transfer_alignment import Case as ErrorCase

class MessageModelTests(unittest.TestCase):
    def test_one_clock_pair_for_two_transfers(self):
        trace,result=expected(Case((TXCase(),RXCase(buffer=0x20031000))))
        self.assertEqual(result,0)
        self.assertEqual([t for t in trace if t[0]=='clock'],[('clock',14,1),('clock',14,0)])
        self.assertIn(('read',TRANSFER+24,TRANSFER+64+24),trace)
        self.assertIn(('write',STATE+20,TRANSFER+64),trace)

    def test_error_skips_later_transfer(self):
        trace,result=expected(Case((ErrorCase(),TXCase(buffer=0x20031000))))
        self.assertEqual(result,0xffffffea)
        self.assertNotIn(('write',STATE+20,TRANSFER+64),trace)

    def test_alias_requires_memory_model(self):
        with self.assertRaisesRegex(ValueError,'shared-memory'):
            expected(Case((RXCase(),TXCase())))

    def test_rx_bytes_feed_later_tx(self):
        trace,_=expected(Case((RXCase(),TXCase(bits=8)),shared_buffers=True))
        writes=[t[2] for t in trace if t[:2]==('write',0xa3000060)]
        self.assertEqual(writes[-4:],[0x78,0x56,0x01,0xef])

    def test_partial_overlap_preserves_other_bytes(self):
        trace,_=expected(Case((RXCase(),TXCase(bits=8,buffer=0x20030002)),shared_buffers=True))
        writes=[t[2] for t in trace if t[:2]==('write',0xa3000060)]
        self.assertEqual(writes[-4:],[0x01,0xef,0x56,0x78])

if __name__=='__main__': unittest.main()
