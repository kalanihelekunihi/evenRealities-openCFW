# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_dw_spi_setup as v

class SetupTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code = v.decode((v.ROOT/'build/gx8002-board/dw-spi-setup-candidate.disassembly.txt').read_text())

    def test_helper_changes_and_overflow(self):
        for case in (v.Case(speed=1,clock=v.MASK), v.Case(speed_after_call=20,mode_after_call=3)):
            self.assertEqual(v.execute(self.code,case),v.expected(case))

    def test_wrong_default_speed_is_detected(self):
        code = self.code.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='lrw' and '0x989680' in args)
        op,args,width = code[pc]
        code[pc] = (op,args.replace('0x989680','0x989681'),width)
        self.assertNotEqual(v.execute(code,v.Case()),v.expected(v.Case()))

    def test_wrong_clock_module_is_rejected(self):
        code = self.code.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='movi' and args=='r0, 14')
        op,args,width = code[pc]
        code[pc] = (op,'r0, 13',width)
        with self.assertRaisesRegex(ValueError,'clock call'):
            v.execute(code,v.Case())

    def test_wrong_state_divider_store_is_detected(self):
        code = self.code.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='st.w' and args=='r2, (r5, 0x8)')
        op,args,width = code[pc]
        code[pc] = (op,'r2, (r5, 0xc)',width)
        self.assertNotEqual(v.execute(code,v.Case()),v.expected(v.Case()))

    def test_preserved_register_corruption_is_rejected(self):
        code = self.code.copy()
        pc = next(pc for pc,(op,args,width) in code.items() if op=='movi' and args=='r3, 2')
        op,args,width = code[pc]
        code[pc] = (op,'r6, 2',width)
        with self.assertRaisesRegex(ValueError,'ABI'):
            v.execute(code,v.Case())

if __name__ == '__main__':
    unittest.main()
