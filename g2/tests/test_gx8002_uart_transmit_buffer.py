# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_buffer import verify
class UartTransmitBufferTest(unittest.TestCase):
    def test_descriptor_dma_and_irq_paths(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],2304)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
