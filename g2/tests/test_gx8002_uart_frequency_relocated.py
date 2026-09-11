# SPDX-License-Identifier: MIT
import unittest
from link_gx8002_uart_configure_source import build,ROOT
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_frequency_relocated import verify
class UartFrequencyRelocatedTest(unittest.TestCase):
    def test_dto_and_divider_register_patterns(self):
        build(include_initialize=True)
        path=ROOT/'build/gx8002-uart-initialize-source/uart.elf'
        elf=Elf32(path.read_bytes(),str(path));code=decode((path.parent/'uart.disassembly.txt').read_text())
        for word in (0,1,0x1ffffff,0x8000000,0xffffffff):
            with self.subTest(word=word):
                result=verify(elf,code,word)
                self.assertFalse(result['source_admitted'])
                self.assertEqual(result['register_word'],word)
if __name__=='__main__':unittest.main()
