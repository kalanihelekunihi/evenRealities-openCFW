#!/usr/bin/env python3
"""Bound native GPIO base-table and BFI arithmetic against selected source."""
from pathlib import Path
import hashlib
import json
import struct

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ELF = HERE / 'boot-coplacement-gpio-mode-data-round/boot.elf'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert blob[0x4302d4-0x410000:0x4302d8-0x410000] == bytes.fromhex('60f38711')
base = struct.unpack_from('<3I', blob, 0x434190-0x410000)
assert base == (0x183, 0x93, 3)

with ELF.open('rb') as file:
    image = ELFFile(file)
    symbol = next(s for s in image.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'opencfw_boot_gpio_mode_bases')
    address = symbol['st_value']
    assert symbol['st_size'] == 12
    source_data = next(segment.data()[address-segment['p_vaddr']:address-segment['p_vaddr']+12]
                       for segment in image.iter_segments()
                       if segment['p_type'] == 'PT_LOAD'
                       and segment['p_vaddr'] <= address
                       and address + 12 <= segment['p_vaddr'] + segment['p_filesz'])
assert struct.unpack('<3I', source_data) == base

for mode in range(256):
    # Native BFI inserts the low two mode bits into positions 6 and 7.
    native = (base[1] & ~0xc0) | ((mode & 3) << 6)
    selected = 0x13 | ((mode & 3) << 6)
    assert native == selected

receipt = {
    'status': 'PASS_GPIO_MODE_BASES_NATIVE_ARITHMETIC',
    'stock_words': [hex(word) for word in base],
    'selected_data_symbol': 'opencfw_boot_gpio_mode_bases',
    'selected_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
    'checked_type2_modes': 256,
    'stock_bfi_pc': '0x4302d4',
    'limits': [
        'Checks the table bytes, exact stock BFI opcode, and all low-byte mode outcomes; not full native registrar execution.',
        'Physical GPIO/power-register behavior and caller descriptor provenance remain separate.',
    ],
}
(HERE / 'boot-gpio-mode-bases-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'checked_type2_modes': 256}))
