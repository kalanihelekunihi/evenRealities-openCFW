#!/usr/bin/env python3
"""Bind stock-checked forced display initialization using the shared state cell."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_init_force_474100.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-display-init-force-474100/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-display-deinit-force-47432c/apollo-main-display-deinit-force-47432c.o'
OUT = G2 / 'build/c-firmware/20261015/main-display-init-force-474100'
OWNED = {'audio_wear_child_474100'}
RESOLVED = {'audio_wear_child_474100'}
IMPORTS = {'audio_cmsis_queue_put', 'audio_log_extended', 'audio_log_flags',
           'audio_uart_buffer_zero', 'audio_uart_display_manager_queue_cell',
           'audio_display_hw_initialized_200744ec', 'audio_log_wake_allowed',
           'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_DISPLAY_INIT_FORCE_474100'
            or oracle['cases'] != 160 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Display force-init evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_init_force_474100.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Display force-init object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 192 or before & OWNED != RESOLVED or not IMPORTS <= provided:
        raise RuntimeError('Display force-init base contract changed')
    linked = OUT / 'apollo-main-display-init-force-474100.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before or len(after) != 191:
        raise RuntimeError('Display force-init link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DISPLAY_INIT_FORCE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': [], 'unresolved_before': 192, 'unresolved_after': 191,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Shared hardware state cell needs final RAM placement and startup ownership; wake, queue and logging behavior are controlled in the oracle.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 192, 191, sha(path))

if __name__ == '__main__': main()
