# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_spi_transfer_rx import Case,expected,REGS

class RXModelTests(unittest.TestCase):
    def test_store_widths_and_increment(self):
        for bits,width,kind,mask in ((8,1,'write8',255),(16,2,'write16',65535),(32,4,'write',0xffffffff)):
            trace,_=expected(Case(bits=bits,length=width*2))
            stores=[t for t in trace if t[0]==kind and 0x20030000<=t[1]<0x20030008]
            self.assertEqual(stores,[(kind,0x20030000,0x12345678&mask),(kind,0x20030000+width,0xabcdef01&mask)])

    def test_chunking(self):
        trace,_=expected(Case(length=6,rx_depth=2,levels=(2,1),words=(1,2,3)))
        self.assertEqual(sum(t==('write',REGS+96,0) for t in trace),2)

    def test_empty_fifo_then_data(self):
        trace,_=expected(Case(levels=(0,2)))
        self.assertIn(('read',REGS+36,0),trace)

    def test_overrun_is_not_success(self):
        with self.assertRaisesRegex(ValueError,'overrun'): expected(Case(levels=(3,)))

    def test_missing_data_is_not_success(self):
        with self.assertRaisesRegex(ValueError,'data script'): expected(Case(words=()))

if __name__=='__main__': unittest.main()
