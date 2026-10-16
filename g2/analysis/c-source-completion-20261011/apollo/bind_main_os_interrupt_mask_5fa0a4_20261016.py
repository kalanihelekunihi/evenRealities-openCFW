#!/usr/bin/env python3
"""Bind the stock-compared BASEPRI mask leaf into Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_interrupt_mask_5fa0a4.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-os-interrupt-mask-5fa0a4/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-os-scheduler-state-bound/apollo-main-os-scheduler-state-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-os-interrupt-mask-bound'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_OS_INTERRUPT_MASK_5FA0A4' or \
            oracle['cases'] != 6 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('interrupt mask stock comparison changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'os_interrupt_mask_5fa0a4.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != {'audio_os_interrupt_mask_5fa0a4'}:
        raise RuntimeError('interrupt mask source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 189 or 'audio_os_interrupt_mask_5fa0a4' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-os-interrupt-mask-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_os_interrupt_mask_5fa0a4'} or \
            after - before or len(after) != 188:
        raise RuntimeError('Apollo main interrupt mask frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_OS_INTERRUPT_MASK_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': ['audio_os_interrupt_mask_5fa0a4'],
        'unresolved_before': 189, 'unresolved_after': 188,
        'imports_resolved': ['audio_os_interrupt_mask_5fa0a4'], 'imports_added': [],
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['Emulated BASEPRI/barrier behavior does not prove physical interrupt timing.',
                   'Final code placement remains open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
