# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_overtime import ROOT,ADDRESS,decode,execute,Case,expected
class SnpuOvertimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-overtime-candidate.disassembly.txt').read_text())
    def run_case(self,case=Case(),code=None):return execute(self.code if code is None else code,ADDRESS,0,case)
    def patch(self,offset,oldop,newop,args):
        c=self.code.copy();pc=ADDRESS+offset;self.assertEqual(c[pc][0],oldop);c[pc]=(newop,args,c[pc][2]);return c
    def test_getter_head_path(self):
        result=self.run_case();self.assertEqual(result,expected(Case()));self.assertTrue(any(r[0]=='head' for r in result[0]))
    def test_previous_command_head_path(self):
        case=Case(previous=0x31000,head=0xfedcba98);trace=self.run_case(case)[0]
        self.assertIn(['read_word',0x20031004,0xfedcba98],trace);self.assertFalse(any(r[0]=='head' for r in trace))
    def test_two_exact_dump_ranges(self):self.assertEqual([r for r in self.run_case()[0] if r[0]=='dump'],[['dump',0x20030000],['dump',0x20030080]])
    def test_restart_order(self):
        names={'disable','reset','init','set_head','enable'}
        self.assertEqual([r[0] for r in self.run_case()[0] if r[0] in names],['disable','reset','init','set_head','enable'])
    def test_live_pointer_mutations_during_printing(self):
        case=Case(pointers=True,changing=True);self.assertEqual(self.run_case(case),expected(case))
    def test_head_survives_restart_clobbers(self):
        case=Case(head=0xffffffff,pointers=True);trace=self.run_case(case)[0];self.assertEqual(next(r[-1] for r in trace if r[0]=='set_head'),0xffffffff)
    def test_byte_type_zero_extends(self):
        for seed in range(256):
            row=next(r for r in self.run_case(Case(seed=seed))[0] if r[0]=='read_byte');self.assertEqual(row[2],(seed^0x20030080)&255)
    def test_wrong_base_index_detected(self):
        c=self.patch(8,'movi','movi','r1, 3');self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_getter_detected(self):
        c=self.patch(0x18,'bsr','bsr','0x10205860')
        with self.assertRaisesRegex(ValueError,'RAM bounds'):self.run_case(code=c)
    def test_wrong_head_restore_detected(self):
        c=self.patch(0x88,'ld.w','ld.w','r1, (r14, 0x0)');self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_reset_pointer_detected(self):
        c=self.patch(0x78,'ld.w','ld.w','r0, (r4, 0x5c4)');self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_next_command_address_detected(self):
        c=self.patch(0x9e,'addi','addi','r2, 1')
        with self.assertRaisesRegex(ValueError,'RAM bounds'):self.run_case(Case(previous=0x31000),c)
    def test_wrong_scratch_size_detected(self):
        c=self.patch(2,'subi','subi','r14, r14, 12')
        with self.assertRaisesRegex(ValueError,'scratch allocation'):self.run_case(code=c)
    def test_wrong_return_frame_detected(self):
        c=self.patch(0x98,'pop','pop','r4-r6, r15')
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(code=c)
if __name__=='__main__':unittest.main()
