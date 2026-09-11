# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_dma_release import verify


class DmaReleaseTest(unittest.TestCase):
    def test_exact_wrapper_and_deallocation_composition(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],384)
        self.assertTrue(result['source_admitted'])
        row=result['functions'][0]
        self.assertEqual(row['compiled_sha256'],row['stock_occurrences'][0]['sha256'])


if __name__=='__main__':unittest.main()
