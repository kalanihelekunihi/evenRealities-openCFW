# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_spi_transfer_lifecycle as v

class TransferLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code=v.decode((v.ROOT/'build/gx8002-board/dw-spi-quick-transfer-candidate.disassembly.txt').read_text())

    def test_busy_and_empty(self):
        for active in (0,v.MESSAGE,0xffffffff):
            self.assertEqual(v.execute(self.code,v.Case(active)),0)

    def test_wrong_initial_message_write_is_rejected(self):
        code=self.code.copy()
        pc=next(pc for pc,(op,args,w) in code.items() if op=='st.w' and args=='r5, (r1, 0x18)')
        op,args,w=code[pc]
        code[pc]=(op,'r5, (r1, 0x1c)',w)
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,v.Case(v.MESSAGE))

    def test_wrong_clock_module_is_rejected(self):
        code=self.code.copy()
        pc=next(pc for pc,(op,args,w) in code.items() if op=='movi' and args=='r0, 14')
        op,args,w=code[pc]
        code[pc]=(op,'r0, 13',w)
        with self.assertRaisesRegex(ValueError,'transaction mismatch'):
            v.execute(code,v.Case())

    def test_clock_hook_matches_lifecycle(self):
        for active,wanted in ((0,[(14,1),(14,0)]),(v.MESSAGE,[])):
            calls=[]
            v.execute(self.code,v.Case(active),clock_hook=lambda module,enable:calls.append((module,enable)))
            self.assertEqual(calls,wanted)

    def test_clock_hook_failure_propagates(self):
        def fail(module,enable): raise ValueError('injected gate mismatch')
        with self.assertRaisesRegex(ValueError,'injected gate mismatch'):
            v.execute(self.code,v.Case(),clock_hook=fail)

if __name__=='__main__': unittest.main()
