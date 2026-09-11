# SPDX-License-Identifier: MIT
import unittest

class FrequencyRewriteTests(unittest.TestCase):
    def test_masked_subband_arithmetic(self):
        original=(61440000,73728000,86016000,98304000)
        for band in range(4):
            self.assertEqual(61440000 + band*12288000,original[band])

    def test_unsigned_module_predicate(self):
        # Above 9 both forms return true; enumerate the entire remaining domain
        # and unsigned boundary examples explicitly.
        for module in (*range(256),0x7fffffff,0x80000000,0xffffffff):
            upstream=module>=10 or module in (6,9,2)
            rewritten=module>=9 or (module & ~4)==2
            self.assertEqual(rewritten,upstream)

if __name__=='__main__':
    unittest.main()
