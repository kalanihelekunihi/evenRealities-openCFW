#!/usr/bin/env python3
"""Bind native Cordio security interface and message handler to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_sec_interface_78a898.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-sec-interface-78a898'
BASE = G2 / 'build/c-firmware/20261015/main-smp-get-stk-537c4c/apollo-main-smp-get-stk-537c4c.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_security_table', 'audio_ble_dm_sec_msg_handler_4d2440'}
EXISTING = {'audio_ble_dm_dispatch_4d2544', 'audio_ble_dm_dispatch_4d2364',
            'dmConnCcbById', 'DmConnSetIdle', 'HciLeStartEncryptionCmd',
            'HciLeLtkReqReplCmd', 'HciLeLtkReqNegReplCmd'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
MESSAGE_SHA = 'e81d46f26d7abdc37bfd9591456c899b262f48cbe9e29b5b103191461d343968'
TABLE_SHA = '480092e342ed56020f154b848f6f5b49b0ddcfbb3ed7f89e8366f979e8cf0403'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x4d2440-0x438000:0x4d24a8-0x438000]).hexdigest() != MESSAGE_SHA or \
            hashlib.sha256(blob[0x78a898-0x438000:0x78a8a4-0x438000]).hexdigest() != TABLE_SHA:
        raise RuntimeError('Apollo DM security interface native bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_SEC_INTERFACE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 36:
        raise RuntimeError('DM security interface oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_sec_interface_78a898.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_security_table' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM security interface source symbols changed')
    linked = OUT / 'apollo-main-dm-sec-interface-78a898.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_security_table'}
    if len(before) != 199 or len(after) != 198 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM security interface link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_SEC_INTERFACE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_message_sha256': MESSAGE_SHA,
               'stock_table_sha256': TABLE_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Native three-slot interface and message handler are C-bound; other DM interfaces, final placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
