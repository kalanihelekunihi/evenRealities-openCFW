# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_setup import build,programs,execute,expected,ADDRESS,MASK


class BoardPinSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):build();cls.code=programs()[1]

    def test_all_success(self):
        self.assertEqual(execute(self.code,ADDRESS,[0]*8),expected([0]*8))

    def test_first_error_still_runs_all_calls(self):
        values=[MASK]+[0]*7
        self.assertEqual(execute(self.code,ADDRESS,values,MASK,37),expected(values))

    def test_wrapped_sum(self):
        values=[MASK,1]+[0]*6
        self.assertEqual(execute(self.code,ADDRESS,values),expected(values))

    def test_wrong_configuration_argument(self):
        code=self.code.copy()
        pc=next(pc for pc,row in code.items() if row[:2]==('movi','r0, 5'))
        code[pc]=('movi','r0, 6',2)
        self.assertNotEqual(execute(code,ADDRESS,[0]*8),expected([0]*8))

    def test_guard_hook_controls_failure_path(self):
        calls=[]
        def fail(pin,mode):
            calls.append((pin,mode))
            return MASK
        result=execute(self.code,ADDRESS,[0]*8,configure_hook=fail)
        self.assertEqual(result,expected([MASK]*8))
        self.assertEqual(len(calls),8)

    def test_cleanup_hook_called_only_on_failure(self):
        calls=[]
        def cleanup(pin,mode):
            calls.append((pin,mode))
            return MASK
        execute(self.code,ADDRESS,[0]*8,set_hook=cleanup)
        self.assertEqual(calls,[])
        execute(self.code,ADDRESS,[MASK]+[0]*7,set_hook=cleanup)
        self.assertEqual(calls,[(5,0),(6,0),(11,0),(12,0)])
