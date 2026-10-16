#!/usr/bin/env python3
"""Bind six-word Apollo display interface and its five queue callbacks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_manager_state_table_776a3c.c'
ORACLE_SCRIPT = G2 / 'analysis/c-source-completion-20261011/apollo/verify_main_display_manager_state_table_776a3c_20261015.py'
ORACLE = G2 / 'build/c-firmware/20261015/main-display-manager-state-table-776a3c/oracle.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-als-sync-registry-4ae73c/apollo-main-als-sync-registry-4ae73c.o'
OUT = G2 / 'build/c-firmware/20261015/main-display-manager-state-table-776a3c'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'g2_display_state_table', 'audio_display_manager_clear_473e2e',
         'audio_display_manager_init_473ea0', 'audio_display_manager_power_up_473f12',
         'audio_display_manager_power_down_473f84', 'audio_display_manager_brightness_473ff6'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    if hashlib.sha256(PAYLOAD.read_bytes()[32:]).hexdigest() != PINNED:
        raise RuntimeError('Apollo payload changed')
    subprocess.run([sys.executable, str(ORACLE_SCRIPT)], check=True,
                   capture_output=True, text=True)
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_BOUNDED_MAIN_DISPLAY_MANAGER_TABLE_NATIVE_C' or \
            len(oracle['cases']) != 60 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('display manager native/C oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_manager_state_table_776a3c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED:
        raise RuntimeError('display manager C providers changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-display-manager-state-table-776a3c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 189 or len(after) != 188 or \
            before-after != {'g2_display_state_table'} or after-before:
        raise RuntimeError('Main display interface import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DISPLAY_MANAGER_TABLE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'native_c_cases': 60, 'interface_words': 6,
               'payload_sha256': PINNED, 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'unresolved_before': 189,
               'unresolved_after': 188, 'imports_resolved': ['g2_display_state_table'],
               'imports_added': [], 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Queue calls, log gates and table slots are compared under controlled inputs; final Main placement and hardware execution are unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
