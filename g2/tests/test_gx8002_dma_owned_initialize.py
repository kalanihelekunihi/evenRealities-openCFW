# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_dma_owned_initialize import verify

class OwnedDmaInitializationTest(unittest.TestCase):
    def test_relocated_initialization_with_clock_and_irq(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],18)
        self.assertEqual([row['bytes'] for row in result['owned_link']['owned_irq_storage']],[256,8])
        self.assertNotIn('open_cfw_gx8002_irq_table',result['owned_link']['external_bindings'])
        self.assertEqual(result['decoded_clock_calls'],36)
        self.assertEqual(result['decoded_irq_calls'],18)
        self.assertEqual(result['registration_boundary_cases'],148)

if __name__=='__main__':
    unittest.main()
