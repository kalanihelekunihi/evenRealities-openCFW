#!/usr/bin/env python3
"""Bind native-backed ALS sync callback, settings setter and display getter."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/als_sync_registry_4ae73c.c'
ORACLE_SCRIPT = G2 / 'analysis/c-source-completion-20261011/apollo/verify_main_als_sync_registry_4ae73c_20261015.py'
ORACLE = G2 / 'build/c-firmware/20261015/main-als-sync-registry-4ae73c/oracle.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-bootloader-flag-7fe000/apollo-main-bootloader-flag-7fe000.o'
OUT = G2 / 'build/c-firmware/20261015/main-als-sync-registry-4ae73c'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'audio_uart_registry_callback_4ae73c',
         'audio_als_settings_set_auto_brightness_46bff4',
         'audio_als_callback_context_47394c'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED:
        raise RuntimeError('Apollo payload changed')
    if int.from_bytes(blob[0x474474-0x438000:0x474478-0x438000], 'little') != 0x776a3c or \
            int.from_bytes(blob[0x46c6a8-0x438000:0x46c6ac-0x438000], 'little') != 0x20072da8:
        raise RuntimeError('ALS display or settings literal changed')
    subprocess.run([sys.executable, str(ORACLE_SCRIPT)], check=True,
                   capture_output=True, text=True)
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_BOUNDED_MAIN_ALS_SYNC_NATIVE_C' or \
            len(oracle['cases']) != 100 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('ALS native/C oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'als_sync_registry_4ae73c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED:
        raise RuntimeError('ALS C providers changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-als-sync-registry-4ae73c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 190 or len(after) != 189 or \
            before-after != {'audio_uart_registry_callback_4ae73c'} or after-before:
        raise RuntimeError('Main ALS import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_ALS_SYNC_REGISTRY_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'native_c_cases': 100, 'logging_masks': [0, 1, 2, 4, 7],
               'payload_sha256': PINNED, 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'unresolved_before': 190,
               'unresolved_after': 189,
               'imports_resolved': ['audio_uart_registry_callback_4ae73c'],
               'imports_added': [], 'source_complete': False,
               'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Oracle covers 100 cases across five log masks; final Main placement and hardware execution remain unproved.',
                          'ROM display table remains unresolved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
