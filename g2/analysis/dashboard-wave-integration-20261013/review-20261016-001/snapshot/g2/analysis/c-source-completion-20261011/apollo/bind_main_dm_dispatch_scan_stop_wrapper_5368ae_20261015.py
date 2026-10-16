#!/usr/bin/env python3
"""Bind the stock eight-byte DM scan-stop forwarding wrapper."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dispatch_scan_stop_wrapper_5368ae.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-stop-wrapper-5368ae'
BASE = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-stop-536896/apollo-main-dm-dispatch-scan-stop-536896.o'
OWNED = {'audio_ble_dm_dispatch_5368ae'}
CHILD = {'audio_ble_dm_dispatch_536896'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    stock = blob[0x5368ae - 0x438000:0x5368b6 - 0x438000]
    if stock != bytes.fromhex('80 b5 ff f7 f1 ff 01 bd'):
        raise RuntimeError('native forwarding body changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_dispatch_scan_stop_wrapper_5368ae.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != CHILD or not CHILD <= symbols(BASE, '--defined-only'):
        raise RuntimeError('DM forwarding wrapper source symbols changed')
    linked = OUT / 'apollo-main-dm-dispatch-scan-stop-wrapper-5368ae.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 206 or len(after) != 205 or \
            before - after != OWNED or after - before:
        raise RuntimeError('DM forwarding wrapper link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_STOP_WRAPPER_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_body_hex': stock.hex(),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The eight-byte native body has one call to 0x536896; that child is separately native-compared.',
                          'Final placement, whole-image link and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
