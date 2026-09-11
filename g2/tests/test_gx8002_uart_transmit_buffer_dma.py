# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_buffer_dma import verify
class UartTransmitBufferDmaTest(unittest.TestCase):
    def test_descriptor_and_stack_argument_handoff(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],72)
        self.assertEqual(result['decoded_setup_calls'],18)
        self.assertEqual(result['decoded_completions'],12)
if __name__=='__main__':unittest.main()
