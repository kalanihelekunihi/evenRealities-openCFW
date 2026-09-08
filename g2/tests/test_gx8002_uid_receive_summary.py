# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_uid_read import ROOT,decode,execute
from model_gx8002_flash_uid_read import expected
from verify_gx8002_uid_receive_step import check_structure,step

class ReceiveSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/uid-read-linked.disassembly.txt').read_text())
    def test_store_mutation_rejected(self):
        code=self.code.copy();op,args,width=code[0x10024182]
        code[0x10024182]=('st.b',args,width)
        with self.assertRaisesRegex(ValueError,'structure changed'):check_structure(code,True)
    def test_branch_mutation_rejected(self):
        code=self.code.copy();code[0x1002416c]=('bt','0x10024180',2)
        with self.assertRaisesRegex(ValueError,'structure changed'):check_structure(code,True)
    def test_summary_without_readiness_rejected(self):
        _,events=expected(0xfffffffe,0xffffffff,0x20029000,0x85,summarize_receive=True)
        with self.assertRaisesRegex(ValueError,'summary precondition'):
            execute(self.code,0x10024104,0,0xfffffffe,0xffffffff,0x20029000,events,
                    summarize_receive=True,summary_status=0)
    def test_empty_step_rejected(self):
        with self.assertRaisesRegex(ValueError,'nonempty precondition'):
            step({},0,1,'r0','r4',0,0,0,0)
    def test_summary_rechecks_structure(self):
        code=self.code.copy();del code[0x1002416a]
        with self.assertRaisesRegex(ValueError,'structure changed'):
            execute(code,0x10024176,0,0,0,1,[],summarize_receive=True)
    def test_incorrect_span_rejected(self):
        _,events=expected(0xfffffffe,0xffffffff,0x20029000,0x85,summarize_receive=True)
        next(e for e in events if e[0]=='receive-span')[2]=1
        with self.assertRaisesRegex(ValueError,'effect mismatch'):
            execute(self.code,0x10024104,0,0xfffffffe,0xffffffff,0x20029000,events,summarize_receive=True)

if __name__=='__main__':unittest.main()
