# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_relocated import verify
class UartTransmitDmaRelocatedTest(unittest.TestCase):
    def test_compiled_source_descriptor_defaults(self):
        result=verify(owned_storage=True)
        self.assertEqual(result['decoded_cases'],36)
        self.assertEqual(result['decoded_callback_calls'],24)
        self.assertEqual(result['decoded_irq_dispatches'],24)
        self.assertEqual(result['decoded_completions'],24)
        self.assertEqual(result['candidate']['external_bindings'],{})

    def test_relocated_setup_and_cleanup(self):
        self.assertEqual(verify()['decoded_cases'],72)
if __name__=='__main__':unittest.main()
