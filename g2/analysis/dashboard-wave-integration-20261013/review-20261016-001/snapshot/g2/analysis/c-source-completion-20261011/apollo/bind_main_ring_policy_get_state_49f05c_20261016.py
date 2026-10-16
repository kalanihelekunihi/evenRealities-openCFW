#!/usr/bin/env python3
"""Bind stock-checked ring policy GetState timeout path."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ring_policy_get_state_49f05c.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-ring-policy-get-state-49f05c/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-ring-connect-policy-on-hand-49f15a/apollo-main-ring-connect-policy-on-hand-49f15a.o'
OUT = G2 / 'build/c-firmware/20261015/main-ring-policy-get-state-49f05c'
OWNED = {'audio_ble_ring_policy_get_state_49f05c'}
IMPORTS = {'audio_ble_ring_policy_state_2007408c', 'audio_ble_ring_policy_tick_now',
           'audio_log_extended', 'audio_log_flags', 'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_RING_POLICY_GET_STATE_49F05C'
            or oracle['cases'] != 256 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Ring GetState oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'ring_policy_get_state_49f05c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Ring GetState object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 191 or before & OWNED != OWNED or not IMPORTS <= provided:
        raise RuntimeError('Ring GetState base contract changed')
    linked = OUT / 'apollo-main-ring-policy-get-state-49f05c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 190:
        raise RuntimeError('Ring GetState link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_RING_POLICY_GET_STATE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 191, 'unresolved_after': 190,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Tick provider and state storage are preexisting C owners; final RAM placement, real clock behavior and hardware execution remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 191, 190, sha(path))

if __name__ == '__main__': main()
