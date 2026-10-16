#!/usr/bin/env python3
"""Bind the native 0x536918 DM stack reset dispatch to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_reset_536918.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-reset-536918'
BASE = G2 / 'build/c-firmware/20261015/main-dm-dispatch-4d2544/apollo-main-dm-dispatch-4d2544.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_stack_reset_536918'}
EXISTING = {'audio_ble_dm_stack_rows_200738dc', 'audio_ble_dm_handler_state',
            'WsfTimerStop', 'audio_ble_dm_stack_state_init'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    stock = blob[0x536918 - 0x438000:0x53694c - 0x438000]
    if hashlib.sha256(stock).hexdigest() != '4c536a89273b5dc06f5da8208450a1a56f5536b1e0ed24e253cebc543f1ad7de':
        raise RuntimeError('native DM stack reset body changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_STACK_RESET_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 21:
        raise RuntimeError('DM stack reset oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_stack_reset_536918.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM stack reset source symbols changed')
    linked = OUT / 'apollo-main-dm-stack-reset-536918.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 203 or len(after) != 202 or \
            before - after != OWNED or after - before:
        raise RuntimeError('DM stack reset link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_RESET_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_body_sha256': hashlib.sha256(stock).hexdigest(),
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The callback event has two native stack bytes with no visible initialization; the C implementation initializes them to zero.',
                          'Final RAM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
