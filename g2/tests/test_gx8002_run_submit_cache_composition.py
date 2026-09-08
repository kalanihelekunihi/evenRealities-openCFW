# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_run_submit_cache_composition as v


class FullPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module in (v.outer.run, v.outer.submit, v.cache.wrapper, v.cache.clean):
            module.verify()
        cls.variants = [pair[1] for pair in v.programs()]

    def execute(self, case, previous=0, variants=None):
        return v.execute(*(variants or self.variants), case, previous, 0)

    def test_new_descriptor_flush_before_enable(self):
        case = v.outer.run.Case(end=8)
        result = self.execute(case)
        self.assertEqual(result, v.expected(case, 0, 0))
        trace = result[0]
        mmio = [i for i, event in enumerate(trace) if event[0] == 'mmio']
        self.assertEqual(len(mmio), 8)
        self.assertLess(mmio[-1], next(i for i, event in enumerate(trace) if event[0] == 'enable'))

    def test_previous_link_store_before_clean(self):
        case = v.outer.run.Case(end=7, state=1)
        result = self.execute(case, 0x20028000)
        self.assertEqual(result, v.expected(case, 0x20028000, 0))
        trace = result[0]
        write = next(i for i, event in enumerate(trace) if event[:2] == ('write', 0x20028004))
        clean = trace.index(('mmio', v.cache.clean.PORT, 0x20028008))
        self.assertLess(write, clean)

    def test_full_ring_emits_no_cache_commands(self):
        trace, words, result = self.execute(v.outer.run.Case(start=0, end=9))
        self.assertEqual(result, 0xffffffff)
        self.assertFalse(any(event[0] == 'mmio' for event in trace))

    def test_wrong_cache_operation_detected(self):
        variants = self.variants.copy()
        code = variants[3][0].copy()
        pc = next(pc for pc, (op, args, width) in code.items() if op == 'ori')
        op, args, width = code[pc]
        code[pc] = (op, 'r3, r0, 10', width)
        variants[3] = (code, *variants[3][1:])
        case = v.outer.run.Case()
        self.assertNotEqual(self.execute(case, variants=variants), v.expected(case, 0, 0))


if __name__ == '__main__':
    unittest.main()
