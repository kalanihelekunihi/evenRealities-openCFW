#!/usr/bin/env python3
"""Bind stock-checked LV RGB888 constructor into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_lv_color_make_441068.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-lv-color-make-441068/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-production-test-screen-event-5cf7f2/apollo-main-production-test-screen-event-5cf7f2.o'
OUT = G2 / 'build/c-firmware/20261015/main-lv-color-make-441068'
OWNED = {'audio_uart_page_441068'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_LV_COLOR_MAKE_441068' or \
            oracle['cases'] != 216 or oracle['source_sha256'] != sha(SOURCE) or \
            oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
        raise RuntimeError('LV RGB888 constructor oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_lv_color_make_441068.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u'):
        raise RuntimeError('LV RGB888 constructor object contract changed')
    before = symbols(BASE, '-u')
    if len(before) != 187 or not OWNED <= before:
        raise RuntimeError('LV RGB888 constructor base frontier changed')
    linked = OUT / 'apollo-main-lv-color-make-441068.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 186:
        raise RuntimeError('LV RGB888 constructor link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_LV_COLOR_MAKE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 187, 'unresolved_after': 186,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Only the defined RGB888 bytes are stock compared; final placement remains open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 187, 186, sha(path))
if __name__ == '__main__': main()
