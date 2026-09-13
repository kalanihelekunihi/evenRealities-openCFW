# SPDX-License-Identifier: MIT
import unittest
from itertools import product
from verify_gx8002_uart_transmit_buffer_dma import verify
from execute_gx8002_linked_uart_transfer import execute
from link_gx8002_dma_uart_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
class UartTransmitBufferDmaTest(unittest.TestCase):
    def test_descriptor_and_stack_argument_handoff(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],72)
        self.assertEqual(result['decoded_setup_calls'],18)
        self.assertEqual(result['decoded_completions'],12)
        self.assertEqual(result['decoded_burst_calls'],24)
        self.assertEqual(result['decoded_cache_calls'],18)
        self.assertEqual(result['decoded_selection_calls'],18)
        self.assertEqual(result['decoded_gate_calls'],12)
        self.assertEqual(result['decoded_clear_calls'],12)
        self.assertEqual(result['decoded_deallocation_calls'],24)
        self.assertEqual(result['decoded_release_calls'],12)
        self.assertEqual(result['decoded_disable_calls'],12)
        self.assertEqual(result['decoded_transfer'],{'transfers':12,'configurations':12,'descriptors':12,'clears':12,'caches':12,'translations':36})
    def test_linked_transfer_descriptor_capacity(self):
        build(owned_dma=True,owned_irq=True,owned_uart=True)
        path=ROOT/'build/gx8002-dma-uart-source/dma-uart.elf'
        elf=Elf32(path.read_bytes(),str(path))
        symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
        code=decode((path.parent/'dma-uart.disassembly.txt').read_text())
        for port,channel,length in product((0,1),(0,1),(0,1,4095,4096,69615,69616,0xffffffff)):
            with self.subTest(port=port,channel=channel,length=length):
                fields=(0,3,0,0,0,0,3,1,7 if port==0 else 5,1,0,1)
                status,counts=execute(code,symbols,0xa0000000+port*0x1000,0x20050000,length,channel,0x20040000,fields)
                accepted=length!=69616
                self.assertEqual(status,0 if accepted else 0xffffffff)
                self.assertEqual(counts['descriptors'],int(accepted))
                self.assertEqual(counts['caches'],int(accepted))
                self.assertEqual(counts['clears'],1)
if __name__=='__main__':unittest.main()
