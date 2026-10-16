#!/usr/bin/env python3
"""Bind Cordio connection reset and its stock default data into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_reset_4b67ec.c'
ORACLE = HERE / 'verify_main_dm_conn_reset_4b67ec_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-reset-4b67ec'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn-message-interfaces-4b6888/apollo-main-dm-conn-message-interfaces-4b6888.o'
OWNED = {'audio_ble_dm_conn_reset_4b67ec', 'audio_ble_dm_conn_spec_defaults_78a814'}
RESOLVED = {'audio_ble_dm_conn_reset_4b67ec'}
EXISTING = {'audio_ble_dm_conn_hci_handler_4b68a4',
            'audio_ble_dm_handler_state', 'audio_dm_connection_records',
            'audio_queue_copy_bytes'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN_RESET_ORACLE' or \
            oracle['cases'] != 72 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('Cordio reset comparison changed')
    obj = OUT / 'display_ble_dm_conn_reset_4b67ec.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not RESOLVED <= before or OWNED & defined or \
            symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING or \
            not EXISTING <= before | defined:
        raise RuntimeError('Cordio reset source symbols changed')
    linked = OUT / 'apollo-main-dm-conn-reset-4b67ec.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 206 or len(after) != 205 or \
            before - after != RESOLVED or after - before:
        raise RuntimeError('Cordio reset link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_RESET_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(RESOLVED), 'imports_added': [],
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
