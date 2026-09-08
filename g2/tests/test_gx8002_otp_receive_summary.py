# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_read import ROOT,decode,execute
from verify_gx8002_otp_receive_step import check_structure,step
class ReceiveSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/otp-read-linked.disassembly.txt').read_text())
    def test_store_mutation_rejected(self):
        code=self.code.copy();op,args,width=code[0x10024090]
        code[0x10024090]=('st.b',args,width)
        with self.assertRaisesRegex(ValueError,'structure changed'):check_structure(code,True)
    def test_branch_mutation_rejected(self):
        code=self.code.copy();code[0x10024096]=('bt','0x1002408e',2)
        with self.assertRaisesRegex(ValueError,'structure changed'):check_structure(code,True)
    def test_summary_without_readiness_rejected(self):
        with self.assertRaisesRegex(ValueError,'readiness precondition'):
            execute({},0,0,0,0,1,[],summarize_receive=True,summary_status=0)
    def test_empty_step_rejected(self):
        with self.assertRaisesRegex(ValueError,'nonempty precondition'):
            step({},0,1,'r9','r3',0,0,0,0)
    def test_summary_rechecks_structure(self):
        code=self.code.copy();del code[0x10024094]
        with self.assertRaisesRegex(ValueError,'structure changed'):
            execute(code,0x10023fa4,0,0,0,1,[],summarize_receive=True)
if __name__=='__main__':unittest.main()
