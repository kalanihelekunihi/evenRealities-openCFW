# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_run_submit_composition as v


class RunSubmitCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.run.verify()
        v.submit.verify()
        cls.runner = (v.run.programs()[1], v.run.ADDRESS, 0)
        cls.publisher = (v.submit.programs()[1], v.submit.ADDRESS, 0)

    def execute(self, case, previous=0, publisher=None):
        model = v.Shared(case, previous, 0, publisher or self.publisher)
        return v.run.execute(*self.runner, case, model=model,
                             call_hook=lambda name, arg, sp, shared:
                             shared.boundary(name, arg, sp))

    def test_descriptor_and_tail_share_memory(self):
        case = v.run.Case(end=4)
        trace, words, result = self.execute(case)
        descriptor = v.run.STATE + 4 * 144 + 16
        self.assertEqual(result, 0)
        self.assertEqual(words[v.run.STATE + 0x5c0], descriptor)
        self.assertEqual(words[descriptor + 4], descriptor & 0xfffffff)
        self.assertIn(('set_head', case.registers, (descriptor + 16) & 0xfffffff), trace)

    def test_append_updates_existing_link(self):
        case = v.run.Case(end=5, state=1)
        trace, words, result = self.execute(case, previous=0x20028000)
        self.assertEqual(words[0x20028004], (v.run.STATE + 5 * 144 + 32) & 0xfffffff)
        self.assertIn(('clean_range', 0x20028000, 8), trace)

    def test_full_ring_does_not_publish(self):
        case = v.run.Case(start=0, end=9)
        trace, words, result = self.execute(case)
        self.assertEqual(result, 0xffffffff)
        self.assertFalse(any(event[0] in ('write', 'submit', 'resume') for event in trace))

    def test_resume_clears_previous_before_publication(self):
        case = v.run.Case(state=2)
        trace, words, result = self.execute(case, previous=0x20028000)
        self.assertIn(('resume',), trace)
        self.assertFalse(any(event[0] == 'clean_range' for event in trace))
        self.assertEqual(words[0x20028004], 0x12345678)

    def test_wrong_nested_head_is_detected(self):
        code = self.publisher[0].copy()
        pc = next(pc for pc, (op, args, width) in code.items() if op == 'addi')
        op, args, width = code[pc]
        code[pc] = (op, 'r5, r0, 12', width)
        case = v.run.Case()
        expected = v.run.expected(case, model=v.Shared(case, 0, 0))
        self.assertNotEqual(self.execute(case, publisher=(code, *self.publisher[1:])), expected)


if __name__ == '__main__':
    unittest.main()
