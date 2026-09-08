# SPDX-License-Identifier: MIT
import sys,unittest,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_enable_state import ROOT,decode,transitions,IE,EE
class EnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(ROOT/'build/gx8002-irq/entry.elf')],text=True))
    def test_duplicate_enable_rejected(self):
        code=self.code.copy();code[0x10025576]=('nie','',2)
        with self.assertRaisesRegex(ValueError,'duplicate NIE'):transitions(code,0,0,0)
    def test_unknown_control_effect_rejected(self):
        code=self.code.copy();code[0x10025576]=('mtcr','r0, cr0',2)
        with self.assertRaisesRegex(ValueError,'unreviewed PSR'):transitions(code,0,0,0)
    def test_callback_can_clear_enable(self):
        rows,result=transitions(self.code,0,0x80000040,0)
        call=next(i for i,r in enumerate(rows) if r['instruction']=='bsr')
        self.assertTrue(all(r['ie_set'] and r['ee_set'] for r in rows[1:call+1]))
        self.assertTrue(all(not r['ie_set'] for r in rows[call+1:]))
        self.assertEqual(result,0x80000040)
    def test_wrong_dispatch_rejected(self):
        code=self.code.copy();pc=next(pc for pc,row in code.items() if row[0]=='bsr');op,args,width=code[pc];code[pc]=(op,'0x10020000',width)
        with self.assertRaisesRegex(ValueError,'dispatch order'):transitions(code,0,0,0)
if __name__=='__main__':unittest.main()
