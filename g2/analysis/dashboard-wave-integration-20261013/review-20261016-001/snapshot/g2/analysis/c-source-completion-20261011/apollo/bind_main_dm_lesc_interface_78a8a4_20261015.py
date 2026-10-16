#!/usr/bin/env python3
"""Bind native Cordio LESC interface, OOB state and message handler to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_lesc_interface_78a8a4.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-lesc-interface-78a8a4'
BASE = G2 / 'build/c-firmware/20261015/main-dm-phy-interface-78a85c/apollo-main-dm-phy-interface-78a85c.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_lesc_table', 'audio_ble_dm_lesc_msg_handler_534894',
         'audio_ble_dm_lesc_oob_rand'}
EXISTING = {'audio_ble_dm_empty_reset_4d29be', 'audio_ble_dm_empty_handler_4d29c0',
            'audio_ble_dm_handler_state', 'WsfBufFree', 'Calc128Cpy'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
HANDLER_SHA = 'b3aab28cc4bd055dbcf5b16010b31396d3cffa3e75f2d1e337b1618fc3898b86'
TABLE_SHA = 'ed14ab53083e48de966c42b4f3ca570a421921b41e002c61dec9ddcab49e85d7'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x534894-0x438000:0x5348ec-0x438000]).hexdigest() != HANDLER_SHA or \
            hashlib.sha256(blob[0x78a8a4-0x438000:0x78a8b0-0x438000]).hexdigest() != TABLE_SHA:
        raise RuntimeError('Apollo DM LESC interface native bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_LESC_INTERFACE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 12:
        raise RuntimeError('DM LESC interface oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_lesc_interface_78a8a4.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_lesc_table' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM LESC interface source symbols changed')
    linked = OUT / 'apollo-main-dm-lesc-interface-78a8a4.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_lesc_table'}
    if len(before) != 197 or len(after) != 196 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM LESC interface link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_LESC_INTERFACE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_handler_sha256': HANDLER_SHA,
               'stock_table_sha256': TABLE_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Native LESC table and bounded message paths are C-bound; OOB pointer final RAM placement and full callback/free behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
