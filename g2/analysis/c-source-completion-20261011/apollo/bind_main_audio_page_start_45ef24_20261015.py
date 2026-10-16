#!/usr/bin/env python3
"""Bind native-compared Apollo audio animation start."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_audio_page_start_45ef24.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-page-start-45ef24'
BASE = G2 / 'build/c-firmware/20261015/main-audio-find-owner-45fcd2/apollo-main-audio-find-owner-45fcd2.o'
ORACLE = HERE / 'verify_main_audio_page_start_45ef24_oracle_20261015.py'
OWNED = {'audio_uart_display_audio_start_45ef24'}
CHILDREN = {
    'audio_uart_display_anim_alpha_45ecbf',
    'audio_uart_display_anim_finish_a_45ee35',
    'audio_uart_display_anim_finish_b_45ed4f',
    'audio_uart_display_anim_finish_c_45eccb',
    'audio_uart_display_anim_finish_d_45ed91',
    'audio_uart_display_anim_x_a_45ecaf',
    'audio_uart_display_anim_y_a_45ecb7',
    'audio_uart_display_audio_prepare_45bbb6',
    'audio_uart_display_audio_reset_441488',
    'audio_uart_lv_obj_x_43fc70',
    'audio_uart_lv_obj_y_43fce0',
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_audio_page_start_45ef24.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / 'oracle.json').read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_START_ORACLE' or \
            oracle['cases'] != 144 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('audio page start oracle changed')
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') - defined - before != CHILDREN:
        raise RuntimeError('audio page start provider contract changed')
    linked = OUT / 'apollo-main-audio-page-start-45ef24.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 211 or len(after) != 221 or \
            before - after != OWNED or after - before != CHILDREN or \
            not OWNED <= symbols(linked, '--defined-only'):
        raise RuntimeError('audio page start linked contract changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_PAGE_START_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'oracle_sha256': sha(OUT / 'oracle.json'),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': sorted(CHILDREN), 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['144 controlled native audio animation branch comparisons.',
                          'Animation and page helper effects are hooked; eleven callbacks/helpers remain.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
