# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_mode import ROOT,decode,execute,expected,memory,STATE,INFOS
class ModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/mode-candidate.disassembly.txt').read_text())
    def test_live_index_after_each_callback(self):
        m=memory();changes=[(1,0),(0,0xffffffff)]
        self.assertEqual(execute(self.code,0x102085a4,m,0,changes),expected(m,0,changes,'init'))
    def test_tick_reads_loop_after_callback(self):
        m=memory();m[STATE]=1
        self.assertEqual(execute(self.code,0x102085f8,m,0,[(1,0)],kind='tick')['result'],0)
    def test_null_tick(self):
        m=memory();m[INFOS[0]+12]=0;m[STATE]=0xffffffff
        self.assertEqual(execute(self.code,0x102085f8,m,0,[],kind='tick'),expected(m,0,[],'tick'))
    def test_wrong_init_flag(self):
        c=self.code.copy();c[0x102085d6]=('movi','r0, 1',4)
        with self.assertRaisesRegex(ValueError,'init flag'):execute(c,0x102085a4,memory(),1,[(None,None)]*2)
    def test_wrong_table_stride(self):
        c=self.code.copy();c[0x102085c8]=('ldr.w','r3, (r5, r3 << 3)',4)
        with self.assertRaisesRegex(ValueError,'callback|read'):execute(c,0x102085a4,memory(),1,[(None,None)]*2)
    def test_missing_frame(self):
        c=self.code.copy();c[0x102085f8]=('mov','r0, r0',2)
        with self.assertRaisesRegex(ValueError,'call frame'):execute(c,0x102085f8,memory(),0,[(None,None)],kind='tick')
    def test_wrong_pop(self):
        c=self.code.copy();c[0x102085e6]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):execute(c,0x102085a4,memory(),1,[(None,None)]*2)
    def test_invalid_callback_index_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError,'read|callback'):execute(self.code,0x102085a4,memory(),0,[(0xffffffff,0),(None,None)])
if __name__=='__main__':unittest.main()
