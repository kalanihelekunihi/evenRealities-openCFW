#!/usr/bin/env python3
"""Bind native-backed tracepoint BLE data decode and dispatch."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_ble_data_5ee8bc.c'
ORACLE_SCRIPT = G2 / 'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_ble_data_5ee8bc_20261015.py'
ORACLE = G2 / 'build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc/oracle.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-tracepoint-registry-5eeec4/apollo-main-tracepoint-registry-5eeec4.o'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'audio_tracepoint_handle_ble_data_5ee8bc'}
ADDED = {'audio_tracepoint_decode_buffer', 'audio_tracepoint_message_descriptor',
         'audio_tracepoint_request_file_name_5ee1f8',
         'audio_tracepoint_delete_file_5ee488', 'audio_tracepoint_delete_all_5ee7b4'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED:
        raise RuntimeError('Apollo payload changed')
    if int.from_bytes(blob[0x5ef020-0x438000:0x5ef024-0x438000], 'little') != 0x2037b9c0 or \
            int.from_bytes(blob[0x5ef024-0x438000:0x5ef028-0x438000], 'little') != 0x77cd84:
        raise RuntimeError('tracepoint RAM or descriptor literal changed')
    subprocess.run([sys.executable, str(ORACLE_SCRIPT)], check=True,
                   capture_output=True, text=True)
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_BOUNDED_MAIN_TRACEPOINT_BLE_DATA_NATIVE_C' or \
            len(oracle['cases']) != 280 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('tracepoint BLE-data native/C oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'tracepoint_ble_data_5ee8bc.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED:
        raise RuntimeError('tracepoint BLE-data C provider changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-tracepoint-ble-data-5ee8bc.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 189 or len(after) != 193 or \
            before-after != OWNED or after-before != ADDED:
        raise RuntimeError('Main tracepoint BLE-data import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_BLE_DATA_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'native_c_cases': 280, 'payload_sha256': PINNED,
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': 189, 'unresolved_after': 193,
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(ADDED),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The live decode buffer, nanopb descriptor and three command children remain imports.',
                          'Nanopb and child effects are compared at call boundaries; final placement and hardware execution are unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
