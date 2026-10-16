#!/usr/bin/env python3
"""Bind the source-owned Cordio DM stack interface record."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_interface_78a88c.c'
ORACLE = HERE / 'verify_main_dm_stack_interface_78a88c_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-interface-78a88c'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn-cb-storage-200712a4/apollo-main-dm-conn-cb-storage-200712a4.o'
OWNED = {'audio_ble_dm_stack_table_78a88c', 'audio_ble_dm_dispatch_table_78a880'}
NEW = {'audio_ble_dm_dispatch_536820',
       'audio_ble_dm_dispatch_536896',
       'audio_ble_dm_dispatch_5368ae',
       'audio_ble_dm_stack_reset_536918',
       'audio_ble_dm_stack_hci_handler_53694c',
       'audio_ble_dm_stack_msg_handler_5369d8',
       'audio_ble_dm_dispatch_4d2544',
       'audio_ble_dm_dispatch_4d2364'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_STACK_INTERFACE_ORACLE' or \
            oracle['record_bytes'] != 32 or \
            oracle['stack_interface_alias_offset'] != 12 or \
            oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('DM stack interface comparison changed')
    obj = OUT / 'display_ble_dm_stack_interface_78a88c.o'
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_stack_table_78a88c' not in before or \
            'audio_ble_dm_dispatch_table_78a880' in before or \
            symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != NEW or NEW & (before | defined):
        raise RuntimeError('DM stack interface source symbols changed')
    linked = OUT / 'apollo-main-dm-stack-interface-78a88c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 200 or len(after) != 207 or \
            before - after != {'audio_ble_dm_stack_table_78a88c'} or \
            after - before != NEW:
        raise RuntimeError('DM stack interface link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_INTERFACE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': ['audio_ble_dm_stack_table_78a88c'],
               'imports_added': sorted(NEW),
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
