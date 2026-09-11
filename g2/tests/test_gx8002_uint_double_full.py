# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uint_double_prepare import verify


class UintDoubleFullTest(unittest.TestCase):
    def test_decoded_conversion_through_return(self):
        result = verify()
        self.assertEqual(result['cases'], 8239)
        self.assertEqual(result['full_function_executions'], 32956)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
