# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_double_fix_tail import verify

class DoubleFixCompositionTest(unittest.TestCase):
    def test_decoded_unpack_to_fix(self):
        result=verify()
        self.assertEqual(result['cases'],8716)
        self.assertEqual(result['composed_executions'],69728)
        self.assertEqual(result['full_function_executions'],34864)
        self.assertFalse(result['source_admitted'])

if __name__=='__main__':
    unittest.main()
