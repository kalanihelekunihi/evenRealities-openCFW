# SPDX-License-Identifier: MIT
import unittest
from build_gx8002_uart_transmit_complete import build
from verify_gx8002_uart_transmit_complete import verify
class UartTransmitCompleteTest(unittest.TestCase):
    def test_completion_order_and_mutation(self):
        result=verify()
        self.assertEqual(result["decoded_cases"],48)
        self.assertTrue(result['source_admitted'])

    def test_authenticated_stock_instruction_identity(self):
        result=build();row=result['functions'][0]
        self.assertEqual(row['compiled_bytes'],32)
        self.assertEqual(row['compiled_sha256'],row['stock_sha256'])
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
