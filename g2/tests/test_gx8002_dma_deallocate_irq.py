# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_dma_deallocate_irq import verify
class DmaDeallocateIrqTest(unittest.TestCase):
    def test_irq_exclusion_and_restore(self):
        self.assertEqual(verify()['decoded_cases'],640)
if __name__=='__main__':unittest.main()
