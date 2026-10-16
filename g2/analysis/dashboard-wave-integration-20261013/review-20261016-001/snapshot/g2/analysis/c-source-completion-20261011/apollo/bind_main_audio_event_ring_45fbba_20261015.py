#!/usr/bin/env python3
"""Bind native-compared Apollo audio ring predicates and dequeue."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_audio_event_ring_45fbba.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-event-ring-45fbba'
BASE = G2 / 'build/c-firmware/20261015/main-audio-anim-finish-b-45ed4e/apollo-main-audio-anim-finish-b-45ed4e.o'
ORACLE = HERE / 'verify_main_audio_event_ring_45fbba_oracle_20261015.py'
OWNED = {'audio_uart_display_audio_ring_empty_45fbba',
         'audio_uart_display_audio_ring_full_45fbd0',
         'audio_uart_display_audio_dequeue_45fc5a'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_audio_event_ring_45fbba.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / 'oracle.json').read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_AUDIO_EVENT_RING_ORACLE' or \
            oracle['cases'] != 192 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('audio ring oracle changed')
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if OWNED & defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') - defined:
        raise RuntimeError('audio ring provider contract changed')
    linked = OUT / 'apollo-main-audio-event-ring-45fbba.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 214 or after != before or \
            not OWNED <= symbols(linked, '--defined-only'):
        raise RuntimeError('audio ring linked contract changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_EVENT_RING_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'oracle_sha256': sha(OUT / 'oracle.json'),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': [],
               'imports_added': [], 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['192 controlled native ring comparisons.',
                          'These are children of the unresolved event dispatcher.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
