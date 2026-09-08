# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_stream_shutdown import ROOT,decode,execute,expected
class StreamShutdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/stream-shutdown-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,pc=0x10206dac):return execute(self.code if code is None else code,pc,0,0xdeadbeef,0xffffffff)
    def test_callback_cleared_after_driver(self):self.assertEqual(self.run_case(),expected('LvpKwsDone',0xdeadbeef))
    def test_audio_returns_zero(self):self.assertEqual(self.run_case(pc=0x102073f8),expected('LvpAudioInDone',0xdeadbeef))
    def test_wrong_callback_slot(self):
        c=self.code.copy();c[0x10206db6]=('st.w','r0, (r3, 0x4)',2)
        with self.assertRaisesRegex(ValueError,'callback address'):self.run_case(c)
    def test_nonzero_callback_and_return(self):
        c=self.code.copy();c[0x10206db4]=('movi','r0, 1',2)
        self.assertNotEqual(self.run_case(c),expected('LvpKwsDone',0xdeadbeef))
    def test_wrong_driver(self):
        c=self.code.copy();c[0x10206dae]=('bsr','0x10204984',4)
        self.assertNotEqual(self.run_case(c),expected('LvpKwsDone',0xdeadbeef))
    def test_audio_must_not_propagate_failure(self):
        c=self.code.copy();c[0x102073fe]=('movi','r3, 0',2)
        self.assertNotEqual(self.run_case(c,pc=0x102073f8),expected('LvpAudioInDone',0xdeadbeef))
    def test_clear_before_driver_detected(self):
        c=self.code.copy();c[0x10206dae]=('lrw','r3, 0x20027b50',4);c[0x10206db2]=('movi','r0, 0',2);c[0x10206db4]=('st.w','r0, (r3, 0x0)',2);c[0x10206db6]=('bsr','0x10205d40',2)
        self.assertNotEqual(self.run_case(c),expected('LvpKwsDone',0xdeadbeef))
    def test_bad_frame(self):
        c=self.code.copy();c[0x10206db8]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
