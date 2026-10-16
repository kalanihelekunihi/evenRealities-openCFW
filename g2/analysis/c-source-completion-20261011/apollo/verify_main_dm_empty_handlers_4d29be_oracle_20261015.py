#!/usr/bin/env python3
"""Compare C no-op handlers with stock two-byte Thumb bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_empty_handlers_4d29be.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_main.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-empty-handlers-4d29be'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ENTRIES = [('audio_ble_dm_empty_reset_4d29be', 'dmEmptyReset', 0x4d29be),
           ('audio_ble_dm_empty_handler_4d29c0', 'dmEmptyHandler', 0x4d29c0)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    for _, name, _ in ENTRIES:
        start = upstream.index('void ' + name + '(')
        body = upstream[start:upstream.index('\n}', start)]
        if name == 'dmEmptyReset' and '/* empty */' not in body:
            raise RuntimeError('Cordio empty reset changed')
        if name == 'dmEmptyHandler' and 'return;' not in body:
            raise RuntimeError('Cordio empty handler changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_empty_handlers_4d29be.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    with obj.open('rb') as f:
        elf = ELFFile(f)
        code = elf.get_section_by_name('.text').data()
        symtab = elf.get_section_by_name('.symtab')
        symbols = {s.name: s for s in symtab.iter_symbols()}
        pairs = []
        for source_name, upstream_name, address in ENTRIES:
            sym = symbols[source_name]
            offset = sym['st_value'] & ~1
            candidate = code[offset:offset + 2]
            stock = blob[address - 0x438000:address - 0x438000 + 2]
            if candidate != stock or stock != b'\x70\x47':
                raise RuntimeError(f'{source_name} Thumb return changed')
            pairs.append({'source_symbol': source_name, 'upstream_name': upstream_name,
                          'stock_address': hex(address), 'thumb_hex': stock.hex()})
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_EMPTY_HANDLERS_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'matching_bodies': pairs, 'cases': 2,
               'limits': ['Individual two-byte Thumb bodies match; compiler alignment differs from stock adjacency.',
                          'The interface table still requires its six nonempty handler bodies and final placement.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 2, sha(path))

if __name__ == '__main__': main()
