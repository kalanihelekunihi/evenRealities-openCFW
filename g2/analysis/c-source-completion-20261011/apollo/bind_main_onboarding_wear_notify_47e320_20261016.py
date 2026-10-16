#!/usr/bin/env python3
"""Bind stock-checked onboarding wear notification and expose its encoder."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/onboarding_wear_notify_47e320.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-onboarding-wear-notify-47e320/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-display-init-force-474100/apollo-main-display-init-force-474100.o'
OUT = G2 / 'build/c-firmware/20261015/main-onboarding-wear-notify-47e320'
OWNED = {'audio_wear_child_47e320'}
RESOLVED = {'audio_wear_child_47e320'}
ADDED = {'audio_onboarding_event_encode_4a8368'}
IMPORTS = {'audio_ota_transfer_active', 'audio_log_wake_allowed',
           'audio_quicklist_refresh_enabled_4434d0',
           'audio_onboarding_event_encode_4a8368',
           'audio_log_flags', 'audio_log_extended', 'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_ONBOARDING_WEAR_NOTIFY_47E320'
            or oracle['cases'] != 360 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Onboarding wear notification evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'onboarding_wear_notify_47e320.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Onboarding wear notification object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if (len(before) != 191 or before & OWNED != RESOLVED or
            not (IMPORTS - ADDED) <= provided or ADDED & (before | provided)):
        raise RuntimeError('Onboarding wear notification base contract changed')
    linked = OUT / 'apollo-main-onboarding-wear-notify-47e320.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before != ADDED or len(after) != 191:
        raise RuntimeError('Onboarding wear notification link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_ONBOARDING_WEAR_NOTIFY_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': sorted(ADDED), 'unresolved_before': 191, 'unresolved_after': 191,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['The stock onboarding protobuf encoder at 0x4a8368 is now exposed and needs a C body; event encoding and transport need qualification.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 191, 191, sha(path))

if __name__ == '__main__': main()
