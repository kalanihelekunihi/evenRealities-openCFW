#!/usr/bin/env python3
"""Bind the native-compared audio display ready transition routine."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_ready_45f8a4.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-ready-45f8a4'
BASE = G2 / 'build/c-firmware/20261015/main-audio-page-queue-45f58c/apollo-main-audio-page-queue-45f58c.o'
ORACLE = HERE / 'verify_main_audio_page_ready_45f8a4_oracle_20261015.py'
OWNED = {'audio_uart_display_audio_ready_45f8a4'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_audio_page_ready_45f8a4.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / 'oracle.json').read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_READY_ORACLE' or \
            oracle['cases'] != 32 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('audio page remove oracle changed')
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') - defined:
        raise RuntimeError('audio page remove provider contract changed')
    linked = OUT / 'apollo-main-audio-page-ready-45f8a4.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 212 or len(after) != 211 or \
            before - after != OWNED or after - before or \
            not OWNED <= symbols(linked, '--defined-only'):
        raise RuntimeError('audio page remove linked contract changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_READY_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'oracle_sha256': sha(OUT / 'oracle.json'),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['32 controlled native ready transition comparisons.',
                          'Live page setter effects and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
