#!/usr/bin/env python3
"""Bind stock-checked running-app getter through its existing C provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/system_close_active_app_get_443504.c'
PROVIDER = G2 / 'components/audio/uart_thread_source_candidate/terminal_running_app_ids.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-system-close-active-app-get-443504/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-system-close-common-data-469d48/apollo-main-system-close-common-data-469d48.o'
OUT = G2 / 'build/c-firmware/20261015/main-system-close-active-app-get-443504'
OWNED = {'audio_system_close_active_app_get_443504'}
IMPORTS = {'audio_get_running_app_ids'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_SYSTEM_CLOSE_ACTIVE_APP_GET_443504'
            or oracle['cases'] != 192 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['provider_sha256'] != sha(PROVIDER)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Running-app getter oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'system_close_active_app_get_443504.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Running-app getter adapter contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 188 or before & OWNED != OWNED or not IMPORTS <= provided:
        raise RuntimeError('Running-app getter base contract changed')
    linked = OUT / 'apollo-main-system-close-active-app-get-443504.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 187:
        raise RuntimeError('Running-app getter link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SYSTEM_CLOSE_ACTIVE_APP_GET_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'provider': str(PROVIDER.relative_to(ROOT)), 'provider_sha256': sha(PROVIDER),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 188, 'unresolved_after': 187,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Existing display state owner is reused; final RAM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 188, 187, sha(path))

if __name__ == '__main__': main()
