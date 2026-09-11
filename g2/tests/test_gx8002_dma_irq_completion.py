# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_dma_irq_completion import verify

class DmaCompletionTest(unittest.TestCase):
    def test_persistent_allocation_and_completion_sequence(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],5120)
        self.assertEqual(result['deallocation_calls'],9216)
        self.assertEqual(result['completion_calls'],3072)
        self.assertFalse(result['source_admitted'])

if __name__=='__main__':
    unittest.main()
