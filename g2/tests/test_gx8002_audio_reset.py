# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_audio_reset import ROOT,ADDRESS,decode,execute,expected
class AudioResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/audio-reset-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,delay=3,prefix=None):return execute(self.code if code is None else code,ADDRESS,0xdeadbeef,'changing',delay,prefix)
    def test_fresh_reads_preserved(self):self.assertEqual(self.run_case(),expected(0xdeadbeef,'changing',3))
    def test_delayed_completion(self):self.assertEqual(self.run_case(delay=63),expected(0xdeadbeef,'changing',63))
    def test_never_ready_prefix(self):self.assertEqual(self.run_case(delay=None,prefix=32),expected(0xdeadbeef,'changing',None,32))
    def test_wrong_reset_bit(self):
        c=self.code.copy();c[ADDRESS+0x18]=('bclri','r1, 30',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_stale_read(self):
        c=self.code.copy();c[ADDRESS+0x24]=('ori','r1, r0, 32768',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_wrong_register(self):
        c=self.code.copy();c[ADDRESS+0x10]=('st.w','r3, (r2, 0x8)',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_poll_wrong_bit(self):
        c=self.code.copy();c[ADDRESS+0x82]=('andi','r3, r1, 512',4)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_skipped_wait(self):
        c=self.code.copy();c[ADDRESS+0x86]=('bez','r3, '+hex(ADDRESS+0x8a),4)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_wrong_return(self):
        c=self.code.copy();c[ADDRESS+0x98]=('movi','r0, 1',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,'changing',3))
    def test_abi_clobber(self):
        c=self.code.copy();c[ADDRESS+0x98]=('movi','r4, 0',2)
        with self.assertRaisesRegex(ValueError,'ABI/frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
