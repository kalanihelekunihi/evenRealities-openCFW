#!/usr/bin/env python3
"""Bind stock-checked ring address sentinel into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ring_address_is_unset_4a26e8.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-ring-address-is-unset-4a26e8/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-setting-dominant-hand-467540/apollo-main-setting-dominant-hand-467540.o'
OUT = G2 / 'build/c-firmware/20261015/main-ring-address-is-unset-4a26e8'
OWNED = {'audio_ring_address_is_unset_4a26e8'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_RING_ADDRESS_IS_UNSET_4A26E8'
            or oracle['cases'] != 91 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Ring address oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'ring_address_is_unset_4a26e8.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u'):
        raise RuntimeError('Ring address object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 192 or before & OWNED != OWNED or provided & OWNED:
        raise RuntimeError('Ring address base contract changed')
    linked = OUT / 'apollo-main-ring-address-is-unset-4a26e8.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 191:
        raise RuntimeError('Ring address link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_RING_ADDRESS_IS_UNSET_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 192, 'unresolved_after': 191,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Final Main RAM and flash placement and physical execution remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 192, 191, sha(path))

if __name__ == '__main__': main()
