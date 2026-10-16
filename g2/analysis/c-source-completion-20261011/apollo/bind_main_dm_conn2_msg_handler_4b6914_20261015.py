#!/usr/bin/env python3
"""Bind the Cordio secondary connection message handler."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_msg_handler_4b6914.c'
ORACLE = HERE / 'verify_main_dm_conn2_msg_handler_4b6914_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-msg-handler-4b6914'
BASE = G2 / 'build/c-firmware/20261015/main-dm-conn-sm-execute-533ef4/apollo-main-dm-conn-sm-execute-533ef4.o'
OWNED = {'audio_ble_dm_conn2_msg_handler_4b6914'}
EXISTING = {'dmConnCcbById'}
NEW = {'audio_ble_hci_read_rssi_cmd_52b63a',
       'audio_ble_hci_remote_conn_param_req_reply_52b0be',
       'audio_ble_hci_remote_conn_param_req_neg_reply_52b146',
       'audio_ble_hci_set_data_len_52b176',
       'audio_ble_hci_write_auth_payload_timeout_52b70c',
       'audio_ble_hci_request_peer_sca_52b87a'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_MSG_HANDLER_ORACLE' or \
            oracle['cases'] != 54 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('Cordio secondary message handler comparison changed')
    obj = OUT / 'display_ble_dm_conn2_msg_handler_4b6914.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING | NEW or \
            not EXISTING <= before | defined or NEW & (before | defined):
        raise RuntimeError('Cordio secondary message handler source symbols changed')
    linked = OUT / 'apollo-main-dm-conn2-msg-handler-4b6914.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 203 or len(after) != 208 or \
            before - after != OWNED or after - before != NEW:
        raise RuntimeError('Cordio secondary message handler link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_MSG_HANDLER_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(NEW),
               'oracle_receipt': str(oracle_path.relative_to(ROOT)),
               'oracle_receipt_sha256': sha(oracle_path),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False, 'limits': oracle['limits']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
