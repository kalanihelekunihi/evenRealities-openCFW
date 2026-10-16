#!/usr/bin/env python3
"""Bind stock-checked silent-mode app command and expose send-to-both."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/silent_mode_set_from_app_46921c.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-silent-mode-set-from-app-46921c/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-onboarding-event-encode-4a8368/apollo-main-onboarding-event-encode-4a8368.o'
OUT = G2 / 'build/c-firmware/20261015/main-silent-mode-set-from-app-46921c'
OWNED = {'audio_silent_mode_set_from_app_46921c', 'audio_silent_mode_showing_ui_2007501f'}
RESOLVED = {'audio_silent_mode_set_from_app_46921c'}
ADDED = {'audio_sync_send_to_both_ext_464f76'}
IMPORTS = {'audio_log_extended', 'audio_log_flags', 'audio_log_wake_allowed',
           'audio_silent_mode_change_from_app', 'audio_silent_mode_status_get',
           'audio_sync_send_to_both_ext_464f76', 'audio_uart_device_role_get',
           'audio_uart_display_active', 'audio_uart_display_background',
           'audio_uart_display_mode', 'audio_uart_master_display_stop',
           'audio_uart_task_delay', 'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_SILENT_MODE_SET_FROM_APP_46921C'
            or oracle['cases'] != 1920 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Silent-mode app command evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'silent_mode_set_from_app_46921c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Silent-mode app object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if (len(before) != 190 or before & OWNED != RESOLVED or
            not (IMPORTS - ADDED) <= provided or ADDED & (before | provided)):
        raise RuntimeError('Silent-mode app base contract changed')
    linked = OUT / 'apollo-main-silent-mode-set-from-app-46921c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before != ADDED or len(after) != 190:
        raise RuntimeError('Silent-mode app link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SILENT_MODE_SET_FROM_APP_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': sorted(ADDED), 'unresolved_before': 190, 'unresolved_after': 190,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['SendDataToBothExt at 0x464f76 is exposed and needs a C body; showing-UI RAM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 190, 190, sha(path))

if __name__ == '__main__': main()
