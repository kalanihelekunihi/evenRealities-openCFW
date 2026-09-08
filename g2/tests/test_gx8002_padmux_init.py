# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_padmux_init as v

class PadmuxInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build();cls.code=v.decode((v.ROOT/'build/gx8002-board/padmux-init-candidate.disassembly.txt').read_text())

    def test_duplicate_uses_first_match(self):
        trace,result=v.execute(self.code,v.ADDRESS,[(3,9),(3,2)])
        self.assertEqual([x for x in trace if x[0]=='set' and x[1]==3],[('set',3,9)])
        self.assertEqual(result,0)

    def test_failed_setters_do_not_stop_initialization(self):
        trace,result=v.execute(self.code,v.ADDRESS,[],result=v.MASK)
        self.assertEqual([x for x in trace if x[0]=='set'],[('set',i,0) for i in range(32)])
        self.assertEqual(result,0)

    def test_null_empty_differs_from_nonnull_empty(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,[],pointer=0),([],v.MASK))
        self.assertEqual(v.execute(self.code,v.ADDRESS,[]),v.expected([]))

    def test_hook_runs_all_pins_despite_failure(self):
        seen=[]
        def hook(pin,function):seen.append((pin,function));return v.MASK
        trace,result=v.execute(self.code,v.ADDRESS,[(1,7)],setter_hook=hook)
        self.assertEqual(seen,[(pin,7 if pin==1 else 0) for pin in range(32)])
        self.assertEqual(result,0)

    def test_null_input_skips_hook(self):
        def hook(*args):raise AssertionError('Unexpected setter')
        self.assertEqual(v.execute(self.code,v.ADDRESS,[],pointer=0,setter_hook=hook),([],v.MASK))

    def test_wrong_setter_target_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='bsr')
        op,args,w=code[pc];code[pc]=(op,'0x102065e0',w)
        with self.assertRaisesRegex(ValueError,'setter target'):v.execute(code,v.ADDRESS,[])

if __name__=='__main__':unittest.main()
