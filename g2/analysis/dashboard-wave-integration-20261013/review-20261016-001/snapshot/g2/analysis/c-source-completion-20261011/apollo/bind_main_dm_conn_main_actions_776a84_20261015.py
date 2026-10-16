#!/usr/bin/env python3
"""Bind source-owned Cordio six-action pointer table into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_main_actions_776a84.c'
ORACLE = HERE / 'verify_main_dm_conn_main_actions_776a84_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-main-actions-776a84'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn-update-trace-entry-4b6532/apollo-main-dm-conn-update-trace-entry-4b6532.o'
OWNED = {'audio_ble_dm_conn_state_table_a'}
CHILDREN = {'audio_ble_dm_conn_sm_act_none_4b63ca',
            'audio_ble_dm_conn_sm_act_close_4b63cc',
            'audio_ble_dm_conn_sm_act_opened_4b63d8',
            'audio_ble_dm_conn_sm_act_failed_4b6488',
            'audio_ble_dm_conn_sm_act_closed_4b64ce',
            'audio_ble_dm_conn_sm_act_hci_updated_4b6508'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN_MAIN_ACTIONS_ORACLE' or \
            oracle['entries'] != 6 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('Cordio action table evidence changed')
    obj = OUT / 'display_ble_dm_conn_main_actions_776a84.o'
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != CHILDREN:
        raise RuntimeError('Cordio action table symbols changed')
    linked = OUT / 'apollo-main-dm-conn-main-actions-776a84.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 205 or len(after) != 210 or \
            before - after != OWNED or after - before != CHILDREN:
        raise RuntimeError('Cordio action table link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_MAIN_ACTIONS_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(CHILDREN),
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
