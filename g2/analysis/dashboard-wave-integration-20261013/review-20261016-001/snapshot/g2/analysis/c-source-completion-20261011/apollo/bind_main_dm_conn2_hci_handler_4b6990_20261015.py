#!/usr/bin/env python3
"""Bind native-compared Cordio secondary HCI event routing."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_hci_handler_4b6990.c'
ORACLE = HERE / 'verify_main_dm_conn2_hci_handler_4b6990_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-hci-handler-4b6990'
BASE = G2 / 'build/c-firmware/20261015/main-ble-hci-conn2-payload-commands/apollo-main-ble-hci-conn2-payload-commands.o'
OWNED = {'audio_ble_dm_conn2_hci_handler_4b6990'}
EXISTING = {'audio_ble_dm_conn_ccb_by_handle_4b601c'}
NEW = {'audio_ble_dm_conn2_act_rssi_read_4b6a38',
       'audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e',
       'audio_ble_dm_conn2_act_data_len_change_4b6ab8',
       'audio_ble_dm_conn2_act_write_auth_to_cmpl_4b6afa',
       'audio_ble_dm_conn2_act_auth_to_expired_4b6b28',
       'audio_ble_dm_conn2_act_read_remote_features_cmpl_4b6b50',
       'audio_ble_dm_conn2_act_read_remote_ver_info_cmpl_4b6bac',
       'audio_ble_dm_conn2_act_req_peer_sca_4b6bee'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_HCI_HANDLER_ORACLE' or \
            oracle['cases'] != 60 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('Cordio secondary HCI handler comparison changed')
    obj = OUT / 'display_ble_dm_conn2_hci_handler_4b6990.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING | NEW or \
            not EXISTING <= before | defined or NEW & (before | defined):
        raise RuntimeError('Cordio secondary HCI handler symbols changed')
    linked = OUT / 'apollo-main-dm-conn2-hci-handler-4b6990.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 202 or len(after) != 209 or \
            before - after != OWNED or after - before != NEW:
        raise RuntimeError('Cordio secondary HCI handler link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_HCI_HANDLER_C',
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
