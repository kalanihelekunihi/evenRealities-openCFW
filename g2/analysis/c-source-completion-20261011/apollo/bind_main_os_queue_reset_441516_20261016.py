#!/usr/bin/env python3
"""Bind stock-compared FreeRTOS queue reset into Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/os_queue_reset_441516.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-os-queue-reset-441516/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-os-queue-initialize-bound/apollo-main-os-queue-initialize-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-os-queue-reset-bound'
ADDED = {'audio_os_list_initialize_45607c'}
EXISTING = {'stock_enter_critical', 'stock_exit_critical', 'audio_yield',
            'opencfw_ready_remove_event_list'}
EXISTING_REVIEW = G2 / 'analysis/rtos-ready-wsf-2026-10-05/REPORT.md'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_OS_QUEUE_RESET_441516' or \
            oracle['cases'] != 80 or oracle['source_sha256'] != sha(SOURCE) or \
            oracle['attributed_upstream_commit'] != 'd213f261b5be6bb29a7cce8b84071706b72f4d53' or \
            oracle['attributed_upstream_sha256'] != sha(ROOT / oracle['attributed_upstream']):
        raise RuntimeError('queue reset stock or upstream evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'os_queue_reset_441516.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != {'audio_os_queue_reset_441516'}:
        raise RuntimeError('queue reset source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 187 or 'audio_os_queue_reset_441516' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    if not EXISTING <= symbols(BASE, '--defined-only'):
        raise RuntimeError('existing critical/yield providers changed')
    linked = OUT / 'apollo-main-os-queue-reset-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_os_queue_reset_441516'} or \
            after - before != ADDED or len(after) != 187:
        raise RuntimeError('Apollo main queue reset frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_OS_QUEUE_RESET_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': ['audio_os_queue_reset_441516'],
        'unresolved_before': 187, 'unresolved_after': 187,
        'imports_resolved': ['audio_os_queue_reset_441516'],
        'imports_added': sorted(ADDED),
        'existing_event_removal_review': str(EXISTING_REVIEW.relative_to(ROOT)),
        'existing_event_removal_review_sha256': sha(EXISTING_REVIEW),
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['Critical entry/exit, yield, and bounded event-list removal resolve to earlier C providers; list initialization remains external.',
                   'Invalid paths are compared only through the interrupt-mask boundary.',
                   'Final heap, RAM placement and physical operation remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
