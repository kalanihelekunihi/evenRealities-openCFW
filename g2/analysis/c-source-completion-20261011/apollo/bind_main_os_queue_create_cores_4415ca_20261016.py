#!/usr/bin/env python3
"""Bind stock-compared FreeRTOS static/dynamic queue creation cores."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_queue_create_cores_4415ca.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-os-queue-create-cores-4415ca/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-os-interrupt-mask-bound/apollo-main-os-interrupt-mask-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-os-queue-create-cores-bound'
OWNED = {'audio_os_mutex_static_core_4415ca', 'audio_os_mutex_dynamic_core_441636'}
ADDED = {'audio_os_queue_initialize_441696'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_OS_QUEUE_CREATE_CORES_4415CA' or \
            oracle['cases'] != 96 or oracle['source_sha256'] != sha(SOURCE) or \
            oracle['attributed_upstream_commit'] != 'd213f261b5be6bb29a7cce8b84071706b72f4d53' or \
            oracle['attributed_upstream_sha256'] != sha(ROOT / oracle['attributed_upstream']):
        raise RuntimeError('queue creation stock or upstream evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'os_queue_create_cores_4415ca.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED:
        raise RuntimeError('queue creation source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 188 or not OWNED <= before:
        raise RuntimeError('Apollo main base frontier changed')
    if 'pvPortMalloc' not in symbols(BASE, '--defined-only'):
        raise RuntimeError('existing heap allocator changed')
    linked = OUT / 'apollo-main-os-queue-create-cores-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before != ADDED or len(after) != 187:
        raise RuntimeError('Apollo main queue creation frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_OS_QUEUE_CREATE_CORES_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': sorted(OWNED),
        'unresolved_before': 188, 'unresolved_after': 187,
        'imports_resolved': sorted(OWNED), 'imports_added': sorted(ADDED),
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['The selected C heap allocator resolves locally; shared queue initialization remains external at this stage.',
                   'Invalid cases are observed only through the interrupt-mask boundary.',
                   'Final RAM placement and physical scheduler behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
