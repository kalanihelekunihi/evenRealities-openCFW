# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_spi_transfer_lifecycle as v
from tools.model_gx8002_spi_transfer_tx import Case as TXCase,expected as tx_model
from tools.model_gx8002_spi_transfer_rx import Case as RXCase,expected as rx_model

class FIFOTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code=v.decode((v.ROOT/'build/gx8002-board/dw-spi-quick-transfer-candidate.disassembly.txt').read_text())

    def mutate(self,op,args,newop,newargs):
        code=self.code.copy()
        pc=next(pc for pc,(o,a,w) in code.items() if o==op and a==args)
        _,_,width=code[pc];code[pc]=(newop,newargs,width)
        return code

    def test_rx_wrong_store_width_fails(self):
        code=self.mutate('stbi.h','r7, (r2)','stbi.b','r7, (r2)')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,RXCase(),rx_model)

    def test_rx_wrong_destination_fails(self):
        code=self.mutate('stbi.b','r7, (r2)','stbi.b','r7, (r3)')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,RXCase(bits=8,length=2),rx_model)

    def test_tx_wrong_fifo_space_fails(self):
        code=self.mutate('min.s32','r12, r12, r1','max.u32','r12, r12, r1')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,TXCase(),tx_model)

    def test_rx_wrong_fifo_count_fails(self):
        code=self.mutate('ld.w','r0, (r0, 0x24)','ld.w','r0, (r0, 0x20)')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,RXCase(),rx_model)

    def test_tx_readiness_mask_fails(self):
        code=self.mutate('andi','r2, r1, 4','andi','r2, r1, 0')
        with self.assertRaises(ValueError):
            v.execute(code,TXCase(),tx_model)

if __name__=='__main__': unittest.main()
