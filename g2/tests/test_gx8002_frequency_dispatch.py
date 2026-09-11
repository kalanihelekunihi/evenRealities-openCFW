# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_frequency_dispatch as v

class FrequencyDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.link();out=v.ROOT/'build/gx8002-clock-frequency'
        cls.code=v.decode((out/'frequency-analysis.disassembly.txt').read_text())
        elf=v.Elf32((out/'frequency-analysis.elf').read_bytes(),'frequency')
        cls.table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency'))

    def run_module(self,module,code=None,table=None):
        return v.execute(self.code if code is None else code,0x10025210,module,self.table if table is None else table,0x11000000,0)

    def test_aliases_and_zero_paths(self):
        for module in (7,8,17,18,20,21,23,24,25):
            self.assertEqual(self.run_module(module),v.expected(module))

    def test_large_unsigned_input_skips_switch(self):
        self.assertEqual(self.run_module(0xffffffff),('lookup',0xffffffff))

    def test_wrong_lookup_target_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='bsr')
        op,args,w=code[pc];code[pc]=(op,'0x10024a48',w)
        with self.assertRaisesRegex(ValueError,'lookup target'):self.run_module(0,code=code)

    def test_swapped_switch_target_changes_result(self):
        table=bytearray(self.table)
        table[0:4]=table[(17-7)*4:(17-7)*4+4]
        self.assertNotEqual(self.run_module(7,table=table),v.expected(7))

if __name__=='__main__':unittest.main()
