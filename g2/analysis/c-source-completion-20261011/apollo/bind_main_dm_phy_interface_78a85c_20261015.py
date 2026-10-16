#!/usr/bin/env python3
"""Bind native Cordio PHY interface and HCI handler to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_phy_interface_78a85c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-phy-interface-78a85c'
BASE = G2 / 'build/c-firmware/20261015/main-dm-sec-interface-78a898/apollo-main-dm-sec-interface-78a898.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_phy_table', 'audio_ble_dm_phy_hci_handler_4c5734'}
EXISTING = {'audio_ble_dm_empty_reset_4d29be', 'audio_ble_dm_empty_handler_4d29c0',
            'audio_ble_dm_conn_ccb_by_handle_4b601c', 'audio_dm_connection_records'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
HANDLER_SHA = 'd2da0534cc18e8081c9d3a8de5daee2ab2070de4b86bd13e5bf88d9b71232d70'
TABLE_SHA = '3794cf8786f7ac1d372238f121ca140d76466e0a6ec54a77f4bd250bcd7de2f3'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x4c5734-0x438000:0x4c5810-0x438000]).hexdigest() != HANDLER_SHA or \
            hashlib.sha256(blob[0x78a85c-0x438000:0x78a868-0x438000]).hexdigest() != TABLE_SHA:
        raise RuntimeError('Apollo DM PHY interface native bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_PHY_INTERFACE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 48:
        raise RuntimeError('DM PHY interface oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_phy_interface_78a85c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_phy_table' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM PHY interface source symbols changed')
    linked = OUT / 'apollo-main-dm-phy-interface-78a85c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_phy_table'}
    if len(before) != 198 or len(after) != 197 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM PHY interface link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PHY_INTERFACE_C',
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
               'limits': ['Native PHY table and bounded HCI handler are C-bound; full callback behavior, final placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
