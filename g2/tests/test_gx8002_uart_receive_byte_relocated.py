# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_receive_byte_relocated import verify
class UartReceiveByteRelocatedTest(unittest.TestCase):
    def test_source_descriptor_byte_receive(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],800)
        self.assertEqual(result['candidate']['unresolved_symbols'],[])
if __name__=='__main__':unittest.main()
