# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_snpu_tcb_init as v

class TcbInitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.old,cls.new=v.programs()

    def test_qualification(self):
        self.assertEqual(self.report['cases'],67)
        self.assertEqual(self.report['writes_per_case'],180)

    def test_untouched_payloads_and_guards(self):
        trace,mem=v.execute(self.new,v.ADDRESS,0x87654321)
        touched={a for a,b in trace}
        self.assertEqual(len(touched),180)
        before=v.memory(0x87654321)
        for address in before:
            if address not in touched:self.assertEqual(mem[address],before[address])

    def test_link_chain(self):
        _,mem=v.execute(self.new,v.ADDRESS,0)
        for task in range(10):
            base=v.STATE+task*144
            for slot in range(8):
                self.assertEqual(mem[base+36+slot*12],(base+44+slot*12)&0xfffffff)
            self.assertEqual(mem[base+128],0x10088)
            self.assertEqual(mem[base+16],0x4100ff)

    def changed(self,op,change):
        code=self.new.copy();pc=next(pc for pc,(name,args,width) in code.items() if name==op)
        name,args,width=code[pc];code[pc]=(name,change(args),width);return code

    def test_wrong_slot_opcode(self):
        code=self.new.copy();pc=next(pc for pc,(op,args,w) in code.items() if op=='addi' and args=='r12, r12, 128')
        op,args,w=code[pc];code[pc]=(op,'r12, r12, 129',w)
        self.assertNotEqual(v.execute(code,v.ADDRESS,0),v.expected(0))

    def test_wrong_mask(self):
        # This fixed state address does not use bit27: force a mutation that
        # actually alters the emitted link, rather than claim false coverage.
        code=self.changed('zext',lambda s:s.replace('27','15'))
        self.assertNotEqual(v.execute(code,v.ADDRESS,0),v.expected(0))

    def test_wrong_loop_count(self):
        code=self.new.copy();pc=next(pc for pc,(op,args,w) in code.items() if op=='movi' and args=='r13, 8')
        op,args,w=code[pc];code[pc]=(op,'r13, 7',w)
        self.assertNotEqual(v.execute(code,v.ADDRESS,0),v.expected(0))

    def test_invalid_state_address(self):
        code=self.changed('lrw',lambda _: 'r0, 0x20028000')
        with self.assertRaisesRegex(ValueError,'bounds'):v.execute(code,v.ADDRESS,0)

    def test_preserved_register_corruption(self):
        code=self.new.copy();pc=next(pc for pc,(op,args,w) in code.items() if op=='rts')
        code[pc]=('movi','r4, 0',2);code[pc+2]=('rts','',2)
        with self.assertRaisesRegex(ValueError,'ABI'):v.execute(code,v.ADDRESS,0)

if __name__=='__main__':unittest.main()
