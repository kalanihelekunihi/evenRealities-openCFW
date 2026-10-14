#!/usr/bin/env python3
"""Check the two C uLED option records against the official flash bytes."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile

source = Path(__file__).with_name('display_driver_uled_options.c')
blob = (Path(__file__).resolve().parents[4] /
        'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
records = {'display_driver_uled_option_type1': 0x70afe4,
           'display_driver_uled_option_type0': 0x70b024}
with tempfile.TemporaryDirectory() as directory:
    obj = Path(directory) / 'options.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55',
                    '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                    '-Wall', '-Wextra', '-Werror', '-O2', '-c', str(source),
                    '-o', str(obj)], check=True)
    with obj.open('rb') as file:
        elf = ELFFile(file)
        symbols = {symbol.name: symbol for symbol in
                   elf.get_section_by_name('.symtab').iter_symbols()}
        for name, address in records.items():
            symbol = symbols[name]
            assert symbol['st_size'] == 64, (name, symbol['st_size'])
            section = elf.get_section(symbol['st_shndx'])
            offset = symbol['st_value'] - section['sh_addr']
            candidate = section.data()[offset:offset + 64]
            native = blob[address - 0x438000:address - 0x438000 + 64]
            assert candidate == native, (name, candidate.hex(), native.hex())
print('PASS_DISPLAY_DRIVER_ULED_OPTIONS_EXACT 2 128')
