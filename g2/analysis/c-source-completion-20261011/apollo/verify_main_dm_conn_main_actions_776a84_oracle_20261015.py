#!/usr/bin/env python3
"""Check Cordio main connection action-set order and stock Thumb targets."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_main_actions_776a84.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-main-actions-776a84'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NAMES = ('audio_ble_dm_conn_sm_act_none_4b63ca',
         'audio_ble_dm_conn_sm_act_close_4b63cc',
         'audio_ble_dm_conn_sm_act_opened_4b63d8',
         'audio_ble_dm_conn_sm_act_failed_4b6488',
         'audio_ble_dm_conn_sm_act_closed_4b64ce',
         'audio_ble_dm_conn_sm_act_hci_updated_4b6508')
UPSTREAM_NAMES = ('dmConnSmActNone', 'dmConnSmActClose',
                  'dmConnSmActConnOpened', 'dmConnSmActConnFailed',
                  'dmConnSmActConnClosed', 'dmConnSmActHciUpdated')
TARGETS = (0x4b63cb, 0x4b63cd, 0x4b63d9, 0x4b6489, 0x4b64cf, 0x4b6509)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    raw = blob[0x776a84 - 0x438000:0x776a84 - 0x438000 + 24]
    stock = tuple(int.from_bytes(raw[i:i+4], 'little') for i in range(0, 24, 4))
    if stock != TARGETS:
        raise RuntimeError('stock Cordio action pointers changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('dmConnActSetMain[]')
    end = upstream.index('};', start)
    declarations = upstream[start:end]
    positions = [declarations.index(name) for name in UPSTREAM_NAMES]
    if positions != sorted(positions):
        raise RuntimeError('Cordio source action order changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_conn_main_actions_776a84.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    with obj.open('rb') as f:
        elf = ELFFile(f)
        rodata = elf.get_section_by_name('.rodata')
        reloc = elf.get_section_by_name('.rel.rodata')
        symtab = elf.get_section(reloc['sh_link'])
        entries = sorted((r['r_offset'], r['r_info_type'],
                          symtab.get_symbol(r['r_info_sym']).name)
                         for r in reloc.iter_relocations())
        if rodata['sh_size'] != 24 or rodata.data() != bytes(24) or \
                entries != [(i * 4, 2, name) for i, name in enumerate(NAMES)]:
            raise RuntimeError('compiled action pointer relocations changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_MAIN_ACTIONS_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'stock_address': '0x776a84', 'stock_words': [hex(x) for x in stock],
               'compiled_object_sha256': sha(obj),
               'compiled_relocation_symbols': list(NAMES), 'entries': 6,
               'limits': ['The six source-owned pointer slots match Cordio order and pinned stock targets. Function bodies and final placement are separately gated.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(entries))

if __name__ == '__main__': main()
