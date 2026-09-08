# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_dw_spi_probe as v

class ProbeTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code=v.decode((v.ROOT/'build/gx8002-board/dw-spi-probe-candidate.disassembly.txt').read_text())

    def mutate(self,op,args,replacement):
        code=self.code.copy()
        pc=next(pc for pc,(o,a,w) in code.items() if o==op and a==args)
        _,_,width=code[pc]
        code[pc]=(op,replacement,width)
        return code

    def test_full_probe_and_existing_depths(self):
        for case in (v.Case(tx_mismatch=0,rx_mismatch=257),v.Case(tx_depth=16,rx_depth=32)):
            self.assertEqual(v.execute(self.code,case),v.expected(case)[1])

    def test_wrong_probe_limit_is_rejected(self):
        code=self.mutate('movi','r2, 128','r2, 127')
        with self.assertRaises(ValueError): v.execute(code,v.Case(tx_mismatch=0))

    def test_wrong_callback_is_rejected(self):
        code=self.mutate('lrw','r2, 0x10206164','r2, 0x10206170')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'): v.execute(code,v.Case())

    def test_wrong_irq_is_rejected(self):
        code=self.mutate('movi','r0, 16','r0, 15')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'): v.execute(code,v.Case(tx_depth=16,rx_depth=16))

    def test_wrong_threshold_reset_is_rejected(self):
        code=self.mutate('st.w','r3, (r1, 0x18)','r3, (r1, 0x1c)')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'): v.execute(code,v.Case())

    def test_missing_busy_wait_is_rejected(self):
        code=self.mutate('andi','r4, r2, 1','r4, r2, 0')
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,v.Case(tx_depth=16,rx_depth=16,status=(0,1,0)))

if __name__=='__main__': unittest.main()
