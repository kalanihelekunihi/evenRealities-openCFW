#!/usr/bin/env python3
"""Bind source-owned tracepoint registry callback and role helper."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_registry_5eeec4.c'
ORACLE_SCRIPT = G2 / 'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_registry_5eeec4_20261015.py'
ORACLE = G2 / 'build/c-firmware/20261015/main-tracepoint-registry-5eeec4/oracle.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-display-manager-state-table-776a3c/apollo-main-display-manager-state-table-776a3c.o'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-registry-5eeec4'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'audio_uart_registry_callback_5eeec4', 'audio_tracepoint_role_char_5edadc'}
RESOLVED = {'audio_uart_registry_callback_5eeec4'}
ADDED = {'audio_tracepoint_handle_ble_data_5ee8bc',
         'audio_tracepoint_handle_slave_file_list_5eeb98'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    if hashlib.sha256(PAYLOAD.read_bytes()[32:]).hexdigest() != PINNED:
        raise RuntimeError('Apollo payload changed')
    subprocess.run([sys.executable, str(ORACLE_SCRIPT)], check=True,
                   capture_output=True, text=True)
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_BOUNDED_MAIN_TRACEPOINT_REGISTRY_NATIVE_C' or \
            len(oracle['cases']) != 160 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('tracepoint native/C oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'tracepoint_registry_5eeec4.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED:
        raise RuntimeError('tracepoint C providers changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-tracepoint-registry-5eeec4.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 188 or len(after) != 189 or before-after != RESOLVED or \
            after-before != ADDED:
        raise RuntimeError('Main tracepoint import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REGISTRY_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'native_c_cases': 160, 'payload_sha256': PINNED,
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': 188, 'unresolved_after': 189,
               'imports_resolved': sorted(RESOLVED), 'imports_added': sorted(ADDED),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Two native tracepoint child handlers remain C import gates.',
                          'Child effects are compared at call boundaries; final placement and hardware execution are unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
