#!/usr/bin/env python3
"""Pin three Cordio interface records to stock Thumb pointers and C relocations."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_interfaces_78a820.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-interfaces-78a820'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
RECORDS = [
    ('audio_ble_dm_conn_table_a', 0x78a820, [
        ('audio_ble_dm_conn_reset_4b67ec', 0x4b67ed),
        ('audio_ble_dm_conn_hci_handler_4b68a4', 0x4b68a5),
        ('audio_ble_dm_conn_msg_handler_4b6888', 0x4b6889)]),
    ('audio_ble_dm_conn_table_b', 0x78a82c, [
        ('audio_ble_dm_empty_reset_4d29be', 0x4d29bf),
        ('audio_ble_dm_conn2_hci_handler_4b6990', 0x4b6991),
        ('audio_ble_dm_conn2_msg_handler_4b6914', 0x4b6915)]),
    ('audio_ble_dm_conn_table_c', 0x78a838, [
        ('audio_ble_dm_empty_reset_4d29be', 0x4d29bf),
        ('audio_ble_dm_empty_handler_4d29c0', 0x4d29c1),
        ('audio_ble_dm_conn_upd_msg_handler_4b6a16', 0x4b6a17)]),
]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    expected_upstream = [
        ('dmConnFcnIf', ['dmConnReset', 'dmConnHciHandler', 'dmConnMsgHandler']),
        ('dmConn2FcnIf', ['dmEmptyReset', 'dmConn2HciHandler', 'dmConn2MsgHandler']),
        ('dmConnUpdFcnIf', ['dmEmptyReset', 'dmEmptyHandler', 'dmConnUpdMsgHandler']),
    ]
    for record, entries in expected_upstream:
        anchor = upstream.index('static const dmFcnIf_t ' + record)
        body = upstream[anchor:upstream.index('};', anchor)]
        candidates = [line.strip().rstrip(',').replace('(dmHciHandler_t) ', '')
                      for line in body.splitlines()]
        if [item for item in candidates if item in entries] != entries:
            raise RuntimeError(f'Cordio {record} order changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_conn_interfaces_78a820.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    with obj.open('rb') as f:
        elf = ELFFile(f)
        section = elf.get_section_by_name('.rodata')
        reloc = elf.get_section_by_name('.rel.rodata')
        symbols = elf.get_section_by_name('.symtab')
        if section is None or reloc is None or symbols is None:
            raise RuntimeError('interface object section layout changed')
        data = section.data()
        offsets = {s.name: s['st_value'] for s in symbols.iter_symbols()}
        refs = {r['r_offset']: symbols.get_symbol(r['r_info_sym']).name
                for r in reloc.iter_relocations()}
        if len(refs) != 9 or len(data) != 36:
            raise RuntimeError('interface relocation count or size changed')
        rows = []
        for i, (name, address, entries) in enumerate(RECORDS):
            if offsets.get(name) != i * 12:
                raise RuntimeError(f'{name} offset changed')
            stock = blob[address - 0x438000:address - 0x438000 + 12]
            pointers = [int.from_bytes(stock[j:j + 4], 'little') for j in (0, 4, 8)]
            for j, (symbol, expected_pointer) in enumerate(entries):
                off = i * 12 + j * 4
                if pointers[j] != expected_pointer or refs.get(off) != symbol or \
                        data[off:off + 4] != b'\0\0\0\0':
                    raise RuntimeError(f'{name} slot {j} changed')
            rows.append({'symbol': name, 'stock_address': hex(address),
                         'stock_hex': stock.hex(), 'pointer_symbols': [x[0] for x in entries],
                         'stock_thumb_pointers': [hex(x) for x in pointers]})
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_INTERFACES_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'records': rows, 'pointer_slots': 9,
               'limits': ['Eight target function bodies remain separate source obligations.',
                          'Stock Thumb pointer order and symbolic C relocations do not prove final placement or execution.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(rows), 9, sha(path))

if __name__ == '__main__': main()
