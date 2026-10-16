#!/usr/bin/env python3
"""Bind bounded stock HUB threshold and its two RAM cells."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/hub_semantic_motion_threshold_4a4e8c.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-hub-semantic-motion-threshold-4a4e8c/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-hub-imu-accel-config-4a52a2/apollo-main-hub-imu-accel-config-4a52a2.o'
OUT = G2 / 'build/c-firmware/20261015/main-hub-semantic-motion-threshold-4a4e8c'
OWNED = {'audio_hub_semantic_motion_threshold_4a4e8c',
         'audio_hub_motion_threshold_cell', 'audio_hub_motion_threshold_sine_cell'}
RESOLVED = {'audio_hub_semantic_motion_threshold_4a4e8c'}
IMPORTS = {'__aeabi_i2d', '__aeabi_dmul', '__aeabi_ddiv', '__aeabi_d2f',
           'audio_uart_float_trig_mode1_50968c'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_HUB_SEMANTIC_MOTION_THRESHOLD_4A4E8C'
            or oracle['cases'] != 22 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('HUB threshold evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'hub_semantic_motion_threshold_4a4e8c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('HUB threshold object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 194 or before & OWNED != RESOLVED or not IMPORTS <= provided:
        raise RuntimeError('HUB threshold base contract changed')
    linked = OUT / 'apollo-main-hub-semantic-motion-threshold-4a4e8c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before or len(after) != 193:
        raise RuntimeError('HUB threshold link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HUB_SEMANTIC_MOTION_THRESHOLD_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': [], 'unresolved_before': 194, 'unresolved_after': 193,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Native double VFP arithmetic was controlled in oracle due Unicorn M-class limitation; RAM placement, whole-image integration and hardware behavior remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 194, 193, sha(path))

if __name__ == '__main__': main()
