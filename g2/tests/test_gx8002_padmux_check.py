# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_padmux_check as v

class PadmuxCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code=v.decode((v.ROOT/'build/gx8002-board/padmux-check-candidate.disassembly.txt').read_text())

    def test_negative_arguments_skip_getter(self):
        for pin,function in ((0xffffffff,0),(0,0x80000000)):
            self.assertEqual(v.execute(self.code,v.ADDRESS,pin,function,0),([],0xffffffff))

    def test_invalid_positive_pin_can_match_255(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,33,255,0xffffffff),([('get',33)],0))

    def test_result_is_truncated(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,0,0,256),([('get',0)],0))

    def test_wrong_getter_target_fails(self):
        code=self.code.copy()
        pc=next(pc for pc,(op,args,w) in code.items() if op=='bsr')
        op,args,w=code[pc];code[pc]=(op,'0x10206590',w)
        with self.assertRaisesRegex(ValueError,'getter target'): v.execute(code,v.ADDRESS,0,0,0)

    def test_getter_hook_result_is_used(self):
        seen=[]
        def hook(pin): seen.append(pin); return 0
        self.assertEqual(v.execute(self.code,v.ADDRESS,0,0,0xffffffff,getter_hook=hook),([('get',0)],0))
        self.assertEqual(seen,[0])

    def test_negative_argument_skips_hook(self):
        def fail(pin): raise AssertionError('Getter must not run')
        self.assertEqual(v.execute(self.code,v.ADDRESS,0xffffffff,0,0,getter_hook=fail),([],0xffffffff))

if __name__=='__main__': unittest.main()
