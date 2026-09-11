# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_initialize_relocated import verify
class UartInitializeRelocatedTest(unittest.TestCase):
    def test_relocated_initialization(self):
        result=verify()
        self.assertEqual(result['cases'],1080)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
