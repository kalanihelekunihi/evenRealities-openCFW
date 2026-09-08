# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_gpio_disable_trigger as v


class DisableTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.old,cls.new=v.programs()

    def mutate(self,op,args):
        code=self.new.copy();pc=next(pc for pc,(o,a,w) in code.items() if o==op)
        _,_,width=code[pc];code[pc]=(op,args,width);return code

    def test_cases(self):self.assertEqual(self.report['cases'],1225)

    def test_pin31_and_invalid(self):
        for port in (31,32,0xffffffff):
            case=v.Case(port=port,seed=0xffffffff)
            self.assertEqual(v.execute(self.new,v.ADDRESS,case),v.expected(case))

    def test_wrong_direction_helper(self):
        with self.assertRaisesRegex(ValueError,'target'):
            v.execute(self.mutate('bsr','0x10205f28'),v.ADDRESS,v.Case())

    def test_wrong_first_clear(self):
        case=v.Case(port=4,seed=0x12345678)
        self.assertNotEqual(v.execute(self.mutate('st.w','r1, (r3, 0x18)'),v.ADDRESS,case),v.expected(case))

    def test_frame_rejected(self):
        with self.assertRaisesRegex(ValueError,'frame'):
            v.execute(self.mutate('pop','r15'),v.ADDRESS,v.Case())


if __name__=='__main__':unittest.main()
