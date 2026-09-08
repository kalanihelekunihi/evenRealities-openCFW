# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_padmux_set as v

class PadmuxSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build()
        cls.code=v.decode((v.ROOT/'build/gx8002-board/padmux-set-candidate.disassembly.txt').read_text())

    def test_invalid_pin_skips_memory_and_helper(self):
        for pin in (33,0x80000000,0xffffffff):
            self.assertEqual(v.execute(self.code,v.ADDRESS,pin,0,0,0),([],v.MASK))

    def test_invalid_function_still_writes(self):
        for function in (16,255,0xffffffff):
            self.assertEqual(v.execute(self.code,v.ADDRESS,32,function,0x12345678,v.MASK),v.expected(32,function,0x12345678,v.MASK))

    def test_hook_observes_written_word_and_original_arguments(self):
        seen=[]
        def hook(pin,function,word): seen.append((pin,function,word));return 0
        trace,result=v.execute(self.code,v.ADDRESS,1,0x123,0xffffffff,v.MASK,hook)
        self.assertEqual(seen,[(1,0x123,0xffffff3f)])
        self.assertEqual(result,0)

    def test_failed_readback_does_not_undo_write(self):
        trace,result=v.execute(self.code,v.ADDRESS,0,3,0,0,
                               lambda pin,function,word: v.MASK)
        self.assertEqual(trace,[('read',0xa0010090,0),('write',0xa0010090,3),('check',0,3)])
        self.assertEqual(result,v.MASK)

    def test_invalid_pin_never_calls_hook(self):
        def fail(*args): raise AssertionError('Unexpected checker')
        self.assertEqual(v.execute(self.code,v.ADDRESS,33,0,0,0,fail),([],v.MASK))

    def test_wrong_checker_target_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='bsr')
        op,args,w=code[pc];code[pc]=(op,'0x102065bc',w)
        with self.assertRaisesRegex(ValueError,'checker target'): v.execute(code,v.ADDRESS,0,0,0,0)

    def test_wrong_address_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='lrw')
        op,args,w=code[pc];code[pc]=(op,args.replace('0x28004024','0x28004025'),w)
        with self.assertRaisesRegex(ValueError,'MMIO address'): v.execute(code,v.ADDRESS,0,0,0,0)

if __name__=='__main__': unittest.main()
