#!/usr/bin/env python3
"""Bind DM scan-start 0x536820 and its LE parameter command to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dispatch_scan_start_536820.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-start-536820'
BASE = G2 / 'build/c-firmware/20261015/main-dm-stack-hci-scan-complete-5368b6/apollo-main-dm-stack-hci-scan-complete-5368b6.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_dispatch_536820', 'audio_ble_hci_le_set_scan_params_52b50a'}
EXISTING = {'audio_ble_dm_stack_rows_200738dc', 'audio_ble_dm_handler_state',
            'audio_ble_hci_cmd_alloc_52ae38', 'audio_ble_hci_cmd_send'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
DISPATCH_SHA = '5d69c80e657a3806077ddf9e36d388aaaaed9af11eb9cf148806968c5d40ffd7'
COMMAND_SHA = '3b0cc3ef9900946df4253c88d30701c574fada1d4778125d29516feeb08d7267'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x536820-0x438000:0x536896-0x438000]).hexdigest() != DISPATCH_SHA or \
            hashlib.sha256(blob[0x52b50a-0x438000:0x52b554-0x438000]).hexdigest() != COMMAND_SHA:
        raise RuntimeError('Apollo DM scan-start native bodies changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_START_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 192:
        raise RuntimeError('DM scan-start oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_dispatch_scan_start_536820.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_dispatch_536820' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM scan-start source symbols changed')
    linked = OUT / 'apollo-main-dm-dispatch-scan-start-536820.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_dispatch_536820'}
    if len(before) != 201 or len(after) != 200 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM scan-start link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_START_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_dispatch_sha256': DISPATCH_SHA,
               'stock_command_sha256': COMMAND_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The fixed scan-index mapping and own-address helper are inlined under the native comparisons.',
                          'Controller effects and final RAM placement remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
