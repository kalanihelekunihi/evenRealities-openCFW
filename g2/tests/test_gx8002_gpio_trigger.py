# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_gpio_trigger as v


class TriggerTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify()
        cls.old,cls.new=v.programs()

    def mutate(self, op, args):
        code=self.new.copy()
        pc=next(pc for pc,(o,a,w) in code.items() if o==op)
        _,_,width=code[pc];code[pc]=(op,args,width)
        return code

    def test_cases(self):self.assertEqual(self.report['cases'],2520)

    def test_null_callback_is_stored(self):
        case=v.Case(callback=0,trigger=5)
        self.assertEqual(v.execute(self.new,v.ADDRESS,case),v.expected(case))

    def test_port32_no_calls(self):
        trace,words,result=v.execute(self.new,v.ADDRESS,v.Case(port=32))
        self.assertEqual((trace,result),([],v.MASK))

    def test_wrong_helper_rejected(self):
        with self.assertRaisesRegex(ValueError,'target'):
            v.execute(self.mutate('bsr','0x10000000'),v.ADDRESS,v.Case())

    def test_wrong_record_store_detected(self):
        case=v.Case(port=1,callback=0x10201100)
        self.assertNotEqual(v.execute(self.mutate('st.w','r6, (r1, 0x4)'),v.ADDRESS,case),v.expected(case))

    def test_wrong_frame_rejected(self):
        with self.assertRaisesRegex(ValueError,'frame'):
            v.execute(self.mutate('pop','r4-r6, r15'),v.ADDRESS,v.Case())


if __name__=='__main__':unittest.main()
