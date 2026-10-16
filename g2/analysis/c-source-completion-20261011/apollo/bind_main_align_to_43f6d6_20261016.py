#!/usr/bin/env python3
"""Bind the stock-compared relative alignment provider into Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_lv_align_to_43f6d6.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-align-to-43f6d6/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-legal-page-builder-bound/apollo-main-legal-page-builder-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-align-to-bound'
LOWER = {'audio_uart_lv_style_base_dir_43efba',
         'audio_uart_lv_style_pad_left_43efc6',
         'audio_uart_lv_style_pad_top_43f022',
         'audio_uart_lv_obj_width_43fd9e',
         'audio_uart_lv_obj_height_43fdda',
         'audio_uart_lv_obj_content_width_43fe16',
         'audio_uart_lv_obj_content_height_43fe70',
         'audio_uart_lv_obj_parent_44dca2',
         'audio_uart_lv_scroll_top_44e4aa',
         'audio_uart_lv_scroll_left_44e586',
         'audio_uart_lv_scroll_right_44e67a'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_ALIGN_TO_43F6D6' or \
            oracle['cases'] != 230 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('alignment native comparison changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_lv_align_to_43f6d6.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != {'audio_uart_page_43f6d6'}:
        raise RuntimeError('alignment source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 182 or 'audio_uart_page_43f6d6' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    if not LOWER <= symbols(BASE, '--defined-only'):
        raise RuntimeError('Apollo main lower alignment providers changed')
    linked = OUT / 'apollo-main-align-to-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_uart_page_43f6d6'} or after - before or len(after) != 181:
        raise RuntimeError('Apollo main alignment frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_ALIGN_TO_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': ['audio_uart_page_43f6d6'],
        'unresolved_before': 182, 'unresolved_after': 181,
        'imports_resolved': ['audio_uart_page_43f6d6'], 'imports_added': [],
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['Eleven lower alignment providers resolve to previously bound C implementations.',
                   'The comparison covers 230 controlled cases, not null assertions or unmodeled object state.',
                   'Final code and RAM placement and physical display behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
