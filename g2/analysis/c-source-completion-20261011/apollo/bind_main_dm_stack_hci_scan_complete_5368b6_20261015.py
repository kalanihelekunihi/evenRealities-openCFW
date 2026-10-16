#!/usr/bin/env python3
"""Bind scan-complete child 0x5368b6 and AD walker 0x4d2a06 to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_hci_scan_complete_5368b6.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-hci-scan-complete-5368b6'
BASE = G2 / 'build/c-firmware/20261015/main-dm-stack-hci-handler-53694c/apollo-main-dm-stack-hci-handler-53694c.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_stack_hci_scan_complete_5368b6', 'audio_ble_dm_find_ad_type_4d2a06'}
EXISTING = {'audio_ble_dm_stack_rows_200738dc', 'audio_ble_dm_handler_state'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CHILD_SHA = 'fb671e0abc6c73ca9cc5bff592387709a6b21056f0b79d4043fec190fe5092ac'
WALKER_SHA = '47788f8d1b0247eaa47865cf2159dc71aa039b526032a36c85d7a50fe8427f51'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x5368b6-0x438000:0x536918-0x438000]).hexdigest() != CHILD_SHA or \
            hashlib.sha256(blob[0x4d2a06-0x438000:0x4d2a46-0x438000]).hexdigest() != WALKER_SHA:
        raise RuntimeError('Apollo DM scan native bodies changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_SCAN_COMPLETE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 144:
        raise RuntimeError('DM scan-complete oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_stack_hci_scan_complete_5368b6.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_stack_hci_scan_complete_5368b6' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM scan-complete source symbols changed')
    linked = OUT / 'apollo-main-dm-stack-hci-scan-complete-5368b6.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_stack_hci_scan_complete_5368b6'}
    if len(before) != 202 or len(after) != 201 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM scan-complete link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_SCAN_COMPLETE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_child_sha256': CHILD_SHA,
               'stock_walker_sha256': WALKER_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The AD walker is compared on bounded valid fields; malformed inputs and live radio behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
