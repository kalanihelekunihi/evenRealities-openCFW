# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_clock_selection as v

class SelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.link()
        cls.code=v.decode((v.ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text())

    def run_selection(self,module,offset,source,values,code=None):
        return v.execute(self.code if code is None else code,True,module,offset,source,values)

    def test_second_read_can_clear_selection(self):
        self.assertEqual(self.run_selection(10,0,1,(1,0)),
                         ([(v.SOURCE,1),(v.SEL,1),(v.SEL,0)],'divider',0))

    def test_32k_short_circuit(self):
        self.assertEqual(self.run_selection(0,4,0,(32,)),
                         ([(v.SOURCE,0),(v.SEL,32)],'divider',32000))

    def test_low_frequency_early_returns(self):
        for module in range(26):
            values=(0,0,0)
            self.assertEqual(self.run_selection(module,4,1<<18,values),
                             v.expected(module,4,1<<18,values))

    def test_changed_second_read_is_detected(self):
        code=self.code.copy()
        op,args,width=code[0x100252dc]
        self.assertEqual(op,'ld.w')
        code[0x100252dc]=('movi','r1, 1',width)
        self.assertNotEqual(self.run_selection(10,0,1,(1,0),code),
                            v.expected(10,0,1,(1,0)))

if __name__=='__main__':
    unittest.main()
