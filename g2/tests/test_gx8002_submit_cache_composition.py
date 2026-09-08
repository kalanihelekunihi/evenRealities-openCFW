# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_submit_cache_composition as v


class SubmitCacheCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.submit.verify()
        v.wrapper.verify()
        v.clean.verify()
        cls.submission = (v.submit.programs()[1], v.submit.ADDRESS, 0)
        cls.wrapper = (v.wrapper.programs()[1], v.wrapper.ADDRESS, 0)
        cls.cleaner = (v.clean.programs()[1], v.clean.ADDRESS)

    def run_case(self, case, submission=None, wrapper=None, cleaner=None):
        return v.composed(submission or self.submission, wrapper or self.wrapper,
                          cleaner or self.cleaner, case)

    @staticmethod
    def mutate(program, op, args):
        code = program[0].copy()
        pc = next(pc for pc, (o, a, w) in code.items() if o == op)
        _, _, width = code[pc]
        code[pc] = (op, args, width)
        return (code, *program[1:])

    def test_empty_tail_cache_precedes_enable(self):
        case = v.submit.Case()
        result = self.run_case(case)
        self.assertEqual(result, v.expected(case))
        names = [event[0] for event in result[0]]
        self.assertEqual(names.count('mmio'), 8)
        self.assertLess(max(i for i, name in enumerate(names) if name == 'mmio'),
                        names.index('enable'))

    def test_running_and_stalled_with_live_mutation(self):
        for state in (1, 2):
            case = v.submit.Case(previous=0x20028000, state=state,
                                 completed=0x40000, mutation=True, seed=0x12345678)
            self.assertEqual(self.run_case(case), v.expected(case))

    def test_wrong_nested_cache_operation_detected(self):
        case = v.submit.Case()
        changed = self.mutate(self.cleaner, 'ori', 'r3, r0, 10')
        self.assertNotEqual(self.run_case(case, cleaner=changed), v.expected(case))

    def test_wrong_nested_descriptor_offset_detected(self):
        case = v.submit.Case()
        changed = self.mutate(self.wrapper, 'addi', 'r0, r4, 12')
        self.assertNotEqual(self.run_case(case, wrapper=changed), v.expected(case))

    def test_wrong_publication_pointer_detected(self):
        case = v.submit.Case()
        changed = self.mutate(self.submission, 'addi', 'r5, r0, 12')
        self.assertNotEqual(self.run_case(case, submission=changed), v.expected(case))

    def test_nested_wrong_mmio_port_rejected(self):
        code = self.cleaner[0].copy()
        pc = next(pc for pc, (op, args, width) in code.items()
                  if op == 'lrw' and args.startswith('r0,'))
        op, args, width = code[pc]
        code[pc] = (op, 'r0, 0xe000f010', width)
        changed = (code, *self.cleaner[1:])
        with self.assertRaisesRegex(ValueError, 'MMIO'):
            self.run_case(v.submit.Case(), cleaner=changed)


if __name__ == '__main__':
    unittest.main()
