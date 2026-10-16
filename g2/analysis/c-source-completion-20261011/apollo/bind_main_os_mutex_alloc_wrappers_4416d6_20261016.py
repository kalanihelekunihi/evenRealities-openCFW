#!/usr/bin/env python3
"""Bind the two stock-compared RTOS mutex allocation wrappers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_mutex_alloc_wrappers_4416d6.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-os-mutex-alloc-wrappers-4416d6/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-os-mutex-new-bound/apollo-main-os-mutex-new-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-os-mutex-alloc-wrappers-bound'
OWNED = {'audio_os_mutex_alloc_dynamic_4416d6', 'audio_os_mutex_alloc_static_4416f0'}
ADDED = {'audio_os_mutex_dynamic_core_441636', 'audio_os_mutex_static_core_4415ca',
         'audio_os_mutex_register_4416b8'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_OS_MUTEX_ALLOC_WRAPPERS_4416D6' or \
            oracle['cases'] != 40 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('mutex wrapper stock comparison changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'os_mutex_alloc_wrappers_4416d6.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED:
        raise RuntimeError('mutex wrapper source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 188 or not OWNED <= before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-os-mutex-alloc-wrappers-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before != ADDED or len(after) != 189:
        raise RuntimeError('Apollo main mutex wrapper frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_OS_MUTEX_ALLOC_WRAPPERS_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': sorted(OWNED),
        'unresolved_before': 188, 'unresolved_after': 189,
        'imports_resolved': sorted(OWNED), 'imports_added': sorted(ADDED),
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['The dynamic/static RTOS core allocators and registration helper remain external.',
                   'Final heap, RAM placement, scheduler and physical operation remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
