#!/usr/bin/env python3
"""Verify fixed NOR controller handle address in stock literals and C object."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == STOCK_SHA
p = argparse.ArgumentParser()
p.add_argument('--object', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.object.open('rb') as f:
    elf = ELFFile(f)
    symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'g2_norflash_controller_handle_20074544')
    assert symbol['st_shndx'] == 'SHN_ABS'
    assert symbol['st_value'] == 0x20074544

disassembler = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
locations = []
for address in (0x470d80, 0x4709d0):
    instruction = next(disassembler.disasm(
        blob[address - 0x437fe0:address - 0x437fe0 + 4], address))
    assert instruction.mnemonic == 'ldr.w'
    offset = int(re.search(r'#(0x[0-9a-f]+)', instruction.op_str).group(1), 16)
    literal = ((address + 4) & ~3) + offset
    value = int.from_bytes(blob[literal - 0x437fe0:literal - 0x437fe0 + 4],
                           'little')
    assert value == 0x20074544
    locations.append({'instruction': hex(address), 'literal': hex(literal),
                      'value': hex(value)})

report = {'status': 'PASS_MAIN_NOR_CONTROLLER_FIXED_SRAM_BINDING',
          'stock_sha256': STOCK_SHA,
          'object_sha256': hashlib.sha256(a.object.read_bytes()).hexdigest(),
          'absolute_symbol': 'g2_norflash_controller_handle_20074544',
          'absolute_address': '0x20074544', 'native_literal_sites': locations,
          'limits': ['This binds a symbol to the observed SRAM address.',
                     'Initialization, ownership and physical NOR operation remain unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'])
