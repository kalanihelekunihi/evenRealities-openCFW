# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_configure import build, programs, execute, expected, ADDRESS, MASK


class BoardPinGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.old, cls.new = programs()

    def check(self, case):
        for code, entry in ((self.old,0xfd68),(self.new,ADDRESS)):
            self.assertEqual(execute(code,entry,*case),expected(*case[:4]))

    def test_pin_two_default(self):
        self.check((2,3,0,0,MASK,37))

    def test_nonzero_initialized_skips_check(self):
        self.check((MASK,MASK,0x80000000,MASK,MASK,MASK))

    def test_conflict_does_not_set(self):
        self.check((33,15,0,MASK,0,37))

    def test_setter_failure_is_ignored(self):
        self.check((3,255,0,0,MASK,MASK))

    def test_wrong_helper_is_rejected(self):
        code = self.new.copy()
        pc = next(pc for pc, row in code.items() if row[0]=='bsr')
        code[pc] = ('bsr','0x102065bc',4)
        with self.assertRaisesRegex(ValueError,'helper target'):
            execute(code,ADDRESS,2,0,0,0,0,0)

    def test_changed_pin_default_is_detected(self):
        code = self.new.copy()
        pc = next(pc for pc, row in code.items() if row[0]=='cmpnei')
        code[pc] = ('cmpnei','r0, 3',2)
        case = (2,0,0,0,0,0)
        self.assertNotEqual(execute(code,ADDRESS,*case),expected(*case[:4]))

    def test_unsaved_register_corruption_is_rejected(self):
        code = self.new.copy()
        pc = next(pc for pc, row in code.items() if row[0]=='mov')
        code[pc] = ('movi','r6, 0',2)
        with self.assertRaisesRegex(ValueError,'ABI'):
            execute(code,ADDRESS,2,0,1,0,0,0)

    def test_check_hook_overrides_placeholder(self):
        case = (2,3,0,0,0,0)
        seen = []
        def reject(pin, mode):
            seen.append((pin, mode))
            return MASK
        result = execute(self.new,ADDRESS,*case,check_hook=reject)
        self.assertEqual(result,expected(2,3,0,MASK))
        self.assertEqual(seen,[(2,0)])

    def test_set_hook_receives_original_arguments(self):
        seen = []
        def fail(pin, mode):
            seen.append((pin, mode))
            return MASK
        result = execute(self.new,ADDRESS,32,255,1,0,0,0,set_hook=fail)
        self.assertEqual(result,expected(32,255,1,0))
        self.assertEqual(seen,[(32,255)])

    def test_printf_hook_preserves_guard_error(self):
        seen = []
        def output(pointer, pin):
            seen.append((pointer, pin))
            return 37
        result = execute(self.new,ADDRESS,MASK,3,0,MASK,0,0,printf_hook=output)
        self.assertEqual(result,expected(MASK,3,0,MASK))
        self.assertEqual(seen,[(0x1020ad4a,MASK)])
