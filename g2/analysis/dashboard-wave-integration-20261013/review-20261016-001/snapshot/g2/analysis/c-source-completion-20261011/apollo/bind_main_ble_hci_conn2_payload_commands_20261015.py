#!/usr/bin/env python3
"""Bind four native-compared Cordio HCI payload builders into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_hci_conn2_payload_commands_52b0be.c'
ORACLE = HERE / 'verify_main_ble_hci_conn2_payload_commands_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-ble-hci-conn2-payload-commands'
BASE = G2 / 'build/c-firmware/20261015/main-ble-hci-request-peer-sca-52b87a/apollo-main-ble-hci-request-peer-sca-52b87a.o'
OWNED = {'audio_ble_hci_remote_conn_param_req_reply_52b0be',
         'audio_ble_hci_remote_conn_param_req_neg_reply_52b146',
         'audio_ble_hci_set_data_len_52b176',
         'audio_ble_hci_write_auth_payload_timeout_52b70c'}
EXISTING_CHILDREN = {'audio_ble_hci_cmd_alloc_52ae38', 'audio_ble_hci_cmd_send'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_HCI_CONN2_PAYLOAD_COMMANDS_ORACLE' or \
            oracle['cases'] != 32 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('HCI payload native comparison changed')
    obj = OUT / 'display_ble_hci_conn2_payload_commands_52b0be.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING_CHILDREN or \
            not EXISTING_CHILDREN <= symbols(BASE, '--defined-only'):
        raise RuntimeError('HCI payload source symbols changed')
    linked = OUT / 'apollo-main-ble-hci-conn2-payload-commands.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 206 or len(after) != 202 or \
            before - after != OWNED or after - before:
        raise RuntimeError('HCI payload link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HCI_CONN2_PAYLOAD_COMMANDS_C',
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
