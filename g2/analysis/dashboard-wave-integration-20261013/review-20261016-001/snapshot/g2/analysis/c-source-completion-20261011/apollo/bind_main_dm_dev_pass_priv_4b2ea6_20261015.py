#!/usr/bin/env python3
"""Bind the bounded Cordio privacy event forwarding function into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_dev_pass_priv_4b2ea6.c'
ORACLE = HERE / 'verify_main_dm_dev_pass_priv_4b2ea6_oracle_20261015.py'
OUT = G2 / 'build/c-firmware/20261015/main-dm-dev-pass-priv-4b2ea6'
BASE = G2 / 'build/c-firmware/20261015/main-dm-ccb-dealloc-4b5ef0/apollo-main-dm-ccb-dealloc-4b5ef0.o'
OWNED = {'audio_ble_dm_dev_pass_priv_4b2ea6'}
EXISTING = {'audio_ble_dm_config', 'audio_ble_hci_vendor_log_enabled_4c9c50',
            'audio_ble_hci_vendor_compare_44b610', 'audio_log_flags',
            'audio_log_extended', 'audio_ble_hci_wsf_trace'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle_path = OUT / 'oracle-receipt.json'
    oracle = json.loads(oracle_path.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_DEV_PASS_PRIV_ORACLE' or \
            oracle['cases'] != 162 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('privacy event native comparison changed')
    obj = OUT / 'display_ble_dm_dev_pass_priv_4b2ea6.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING or \
            not EXISTING <= symbols(BASE, '--defined-only'):
        raise RuntimeError('privacy event source symbols changed')
    linked = OUT / 'apollo-main-dm-dev-pass-priv-4b2ea6.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 207 or len(after) != 206 or \
            before - after != OWNED or after - before:
        raise RuntimeError('privacy event link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_DEV_PASS_PRIV_C',
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
