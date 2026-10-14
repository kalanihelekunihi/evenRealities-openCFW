#!/usr/bin/env python3
"""Verify seven C display constants equal authenticated Apollo ROM words."""
from pathlib import Path
import hashlib, json, struct, subprocess
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_hardware_constants.c'
blob = OTA.read_bytes()
ota_hash = hashlib.sha256(blob).hexdigest()
assert ota_hash == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw = blob[0x20:]
cells = {
    'audio_uart_display_board_mmio': (0x44d320, 0x2006f548),
    'audio_uart_display_engine_mmio': (0x471ed0, 0x40008000),
    'audio_uart_display_format_mask': (0x471ecc, 0x0001ff00),
    'audio_uart_display_enable_word': (0x471edc, 0x40008060),
    'audio_uart_display_pin_low': (0x442cd0, 0xe000ed18),
    'audio_uart_display_pin_high': (0x442ccc, 0xe000e400),
    'audio_uart_display_pin_set': (0x442cc8, 0xe000e100),
}
for address, expected in cells.values():
    assert struct.unpack_from('<I', raw, address - 0x438000)[0] == expected
obj = OUT / 'display-hardware-constants.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-std=c11', '-ffreestanding', '-O2', '-Wall', '-Wextra', '-Werror',
                '-c', str(SOURCE), '-o', str(obj)], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {sym.name: sym for sym in elf.get_section_by_name('.symtab').iter_symbols()}
    for name, (_, expected) in cells.items():
        sym = symbols[name]
        section = elf.get_section(sym['st_shndx'])
        assert sym['st_size'] == 4 and section['sh_type'] == 'SHT_PROGBITS'
        actual = struct.unpack_from('<I', section.data(), sym['st_value'])[0]
        assert actual == expected, (name, hex(actual), hex(expected))
result = {
    'status': 'PASS_DISPLAY_HARDWARE_CONSTANTS_BOUNDED',
    'ota_sha256': ota_hash,
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
    'cells': {name: {'rom_word': hex(address), 'value': hex(value)}
              for name, (address, value) in cells.items()},
    'limits': 'Literal equivalence in relocatable C; final linker placement and device register behavior unproven.',
}
(OUT / 'display-hardware-constants-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cells))
