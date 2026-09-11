# SPDX-License-Identifier: MIT
import unittest
from link_gx8002_dma_uart_source import build

class DmaUartSourceLinkTest(unittest.TestCase):
    def test_all_runtime_storage_has_source_definitions(self):
        try:
            report=build(owned_dma=True,owned_irq=True,owned_uart=True)
            self.assertEqual(report['external_bindings'],{})
            self.assertEqual(report['owned_uart_storage'][0]['bytes'],256)
            self.assertTrue(report['owned_uart_storage'][0]['compiled_defaults_verified'])
            self.assertEqual(report['unresolved_symbols'],[])
        finally:
            build()

    def test_source_owned_dma_storage(self):
        try:
            report=build(owned_dma=True)
            self.assertEqual([row['bytes'] for row in report['owned_dma_storage']],[884,16])
            for name in ('dma_state','dma_callbacks'):
                self.assertNotIn('open_cfw_gx8002_'+name,report['external_bindings'])
        finally:
            build()

    def test_callback_storage_relocates_for_writer_and_reader(self):
        try:
            report=build(callback_address=0x20090000)
            self.assertEqual([item['address'] for item in report['callback_storage']],[0x20090000]*2)
        finally:
            build()

    def test_irq_dependencies_resolve_to_source(self):
        report=build()
        self.assertEqual(report['source_count'],25)
        self.assertEqual(len(report['irq_source_calls']),5)
        self.assertEqual(len(report['transmit_source_calls']),3)
        self.assertNotEqual(report['transmit_completion_address'],0x102030c4)
        self.assertEqual(report['unresolved_symbols'],[])
        for name in ('request_irq','irq_save','irq_restore','dma_resource'):
            self.assertNotIn('open_cfw_gx8002_'+name,report['external_bindings'])
        self.assertNotEqual(report['dma_irq_handler_pointer'],0x10203adc)
        self.assertFalse(report['firmware_image'])

if __name__=='__main__':
    unittest.main()
