#!/usr/bin/env python3
"""Bind stock-compared CMSIS IRQ_Context into Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_irq_context_44900e.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-os-irq-context-44900e/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-os-mutex-register-bound/apollo-main-os-mutex-register-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-os-irq-context-bound'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_OS_IRQ_CONTEXT_44900E' or \
            oracle['cases'] != 36 or oracle['source_sha256'] != sha(SOURCE) or \
            oracle['attributed_upstream_commit'] != 'd213f261b5be6bb29a7cce8b84071706b72f4d53' or \
            oracle['attributed_upstream_sha256'] != sha(ROOT / oracle['attributed_upstream']):
        raise RuntimeError('IRQ_Context stock or upstream evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'os_irq_context_44900e.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != {'audio_os_irq_context_44900e'}:
        raise RuntimeError('IRQ_Context source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 188 or 'audio_os_irq_context_44900e' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-os-irq-context-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_os_irq_context_44900e'} or \
            after - before != {'audio_os_scheduler_state_4558a4'} or len(after) != 188:
        raise RuntimeError('Apollo main IRQ_Context frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_OS_IRQ_CONTEXT_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': ['audio_os_irq_context_44900e'],
        'unresolved_before': 188, 'unresolved_after': 188,
        'imports_resolved': ['audio_os_irq_context_44900e'],
        'imports_added': ['audio_os_scheduler_state_4558a4'],
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['Scheduler state remains external.',
                   'Cortex-M register oracle does not prove physical timing or final placement.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
