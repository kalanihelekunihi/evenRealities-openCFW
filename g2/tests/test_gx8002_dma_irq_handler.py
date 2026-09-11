# SPDX-License-Identifier: MIT
"""Stock/source interrupt sequencing and native candidate build regression."""
import unittest
from verify_gx8002_dma_irq_handler import verify

class DmaInterruptTest(unittest.TestCase):
    def test_decoded_stock_source_and_independent_order(self):
        report=verify()
        self.assertEqual(report['decoded_cases'],168)
        self.assertTrue(report['candidate']['functions'][0]['fits'])
        self.assertFalse(report['source_admitted'])

if __name__=='__main__':
    unittest.main()
