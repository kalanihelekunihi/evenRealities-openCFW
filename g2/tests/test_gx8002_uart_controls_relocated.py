# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_controls_relocated import verify
class UartControlsRelocatedTest(unittest.TestCase):
    def test_relocated_control_traces(self):
        result=verify()
        self.assertEqual(result['cases'],576)
        self.assertEqual(result['irq_calls'],864)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
