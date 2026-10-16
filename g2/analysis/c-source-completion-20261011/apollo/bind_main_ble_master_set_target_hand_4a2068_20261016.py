#!/usr/bin/env python3
"""Bind stock-checked target setter through the existing C provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_master_set_target_hand_4a2068.c'
PROVIDER = G2 / 'components/audio/uart_thread_source_candidate/display_ble_master_connect_children.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-ble-master-set-target-hand-4a2068/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-ring-policy-get-state-49f05c/apollo-main-ring-policy-get-state-49f05c.o'
OUT = G2 / 'build/c-firmware/20261015/main-ble-master-set-target-hand-4a2068'
OWNED = {'audio_ble_master_set_target_hand_4a2068'}
IMPORTS = {'audio_ble_master_set_target'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_BLE_MASTER_SET_TARGET_HAND_4A2068'
            or oracle['cases'] != 80 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['provider_sha256'] != sha(PROVIDER)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Target setter oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'ble_master_set_target_hand_4a2068.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Target setter adapter object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 190 or before & OWNED != OWNED or not IMPORTS <= provided:
        raise RuntimeError('Target setter base contract changed')
    linked = OUT / 'apollo-main-ble-master-set-target-hand-4a2068.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 189:
        raise RuntimeError('Target setter link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_BLE_MASTER_SET_TARGET_HAND_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'provider': str(PROVIDER.relative_to(ROOT)), 'provider_sha256': sha(PROVIDER),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 190, 'unresolved_after': 189,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Target storage and provider predate this adapter; final RAM placement and hardware execution remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 190, 189, sha(path))

if __name__ == '__main__': main()
