#!/usr/bin/env python3
"""Bind native-compared Apollo audio animation mode setters."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_audio_set_animation_mode_45fe10.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-set-mode-45fe10'
BASE = G2 / 'build/c-firmware/20261015/main-audio-scheduler-44228a/apollo-main-audio-scheduler-44228a.o'
ORACLE = HERE / 'verify_main_audio_set_mode_45fe10_oracle_20261015.py'
OWNED = {'audio_uart_display_audio_set_mode_child_45fe10',
         'audio_uart_display_audio_set_mode_45fe32'}
RESOLVED = {'audio_uart_display_audio_set_mode_45fe32'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_audio_set_animation_mode_45fe10.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / 'oracle.json').read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_AUDIO_SET_MODE_ORACLE' or \
            oracle['cases'] != 360 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('audio set-mode oracle changed')
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not RESOLVED <= before or OWNED & defined or \
            symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') - defined - before:
        raise RuntimeError('audio set-mode provider contract changed')
    linked = OUT / 'apollo-main-audio-set-mode-45fe10.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 210 or len(after) != 209 or \
            before - after != RESOLVED or after - before or \
            not OWNED <= symbols(linked, '--defined-only'):
        raise RuntimeError('audio set-mode linked contract changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_SET_MODE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'oracle_sha256': sha(OUT / 'oracle.json'),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': [], 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['360 native direct/public setter and logging comparisons.',
                          'Live PageManager effects remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
