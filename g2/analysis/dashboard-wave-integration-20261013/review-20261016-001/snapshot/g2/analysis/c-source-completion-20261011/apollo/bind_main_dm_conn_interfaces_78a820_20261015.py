#!/usr/bin/env python3
"""Bind stock Cordio connection function interfaces into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_interfaces_78a820.c'
ORACLE = HERE / 'verify_main_dm_conn_interfaces_78a820_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-interfaces-78a820'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn-opened-4b63d8/apollo-main-dm-conn-opened-4b63d8.o'
OWNED = {'audio_ble_dm_conn_table_a', 'audio_ble_dm_conn_table_b',
         'audio_ble_dm_conn_table_c'}
TARGETS = {'audio_ble_dm_conn_reset_4b67ec',
           'audio_ble_dm_conn_hci_handler_4b68a4',
           'audio_ble_dm_conn_msg_handler_4b6888',
           'audio_ble_dm_empty_reset_4d29be',
           'audio_ble_dm_conn2_hci_handler_4b6990',
           'audio_ble_dm_conn2_msg_handler_4b6914',
           'audio_ble_dm_empty_handler_4d29c0',
           'audio_ble_dm_conn_upd_msg_handler_4b6a16'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN_INTERFACES_ORACLE' or \
            oracle['pointer_slots'] != 9 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('Cordio interface comparison changed')
    obj = OUT / 'display_ble_dm_conn_interfaces_78a820.o'
    if oracle['object_sha256'] != sha(obj):
        raise RuntimeError('Cordio interface object changed')
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != TARGETS or TARGETS & (before | symbols(BASE, '--defined-only')):
        raise RuntimeError('Cordio interface source symbol frontier changed')
    linked = OUT / 'apollo-main-dm-conn-interfaces-78a820.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 204 or len(after) != 209 or \
            before - after != OWNED or after - before != TARGETS:
        raise RuntimeError('Cordio interface link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_INTERFACES_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(TARGETS),
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
