# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_spi_register_master as v


class SPIRegistrationTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.old,cls.new=v.programs()

    def test_cases(self):self.assertEqual(self.report['cases'],2593)

    def test_nonempty_lists(self):
        case=v.Case(old_count=3,flashes=((1,0),(0,2),(0,1)),selects=2)
        self.assertEqual(v.execute(self.new,v.ADDRESS,case),v.expected(case))

    def test_wrong_list_entry_offset(self):
        code=self.new.copy();pc=next(pc for pc,(op,args,width) in code.items() if op=='ld.w' and args=='r1, (r2, 0x4)');op,args,width=code[pc]
        code[pc]=(op,'r1, (r2, 0x0)',width)
        case=v.Case(old_count=2)
        self.assertNotEqual(v.execute(code,v.ADDRESS,case),v.expected(case))

    def test_wrong_chip_select_comparison(self):
        code=self.new.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='cmphs')
        _,args,width=code[pc];code[pc]=('cmpne',args,width)
        case=v.Case(selects=2,flashes=((0,1),))
        self.assertNotEqual(v.execute(code,v.ADDRESS,case),v.expected(case))

    def test_abi_corruption_rejected(self):
        code=self.new.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='movi')
        op,args,width=code[pc];code[pc]=(op,'r4, 0',width)
        with self.assertRaisesRegex(ValueError,'ABI'):v.execute(code,v.ADDRESS,v.Case())


if __name__=='__main__':unittest.main()
