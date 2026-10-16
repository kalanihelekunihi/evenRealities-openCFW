#!/usr/bin/env python3
"""Bind native-compared RSSI and remote parameter callback actions."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_actions_rssi_param_4b6a38.c'
ORACLE = HERE / 'verify_main_dm_conn2_actions_rssi_param_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-actions-rssi-param-4b6a38'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn2-hci-handler-4b6990/apollo-main-dm-conn2-hci-handler-4b6990.o'
OWNED = {'audio_ble_dm_conn2_act_rssi_read_4b6a38',
         'audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e'}
EXISTING = {'audio_dm_connection_records'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_ACTIONS_RSSI_PARAM_ORACLE' or \
            oracle['cases'] != 32 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('secondary HCI callback comparison changed')
    obj = OUT / 'display_ble_dm_conn2_actions_rssi_param_4b6a38.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING or \
            not EXISTING <= symbols(BASE, '--defined-only'):
        raise RuntimeError('secondary HCI callback source symbols changed')
    linked = OUT / 'apollo-main-dm-conn2-actions-rssi-param-4b6a38.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 209 or len(after) != 207 or \
            before - after != OWNED or after - before:
        raise RuntimeError('secondary HCI callback link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_ACTIONS_RSSI_PARAM_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
