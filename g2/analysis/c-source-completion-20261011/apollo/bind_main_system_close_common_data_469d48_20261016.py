#!/usr/bin/env python3
"""Bind stock-checked system-close common-data registry callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/system_close_common_data_469d48.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-system-close-common-data-469d48/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-ring-policy-schedule-timeouts-49f4a8-49f552/apollo-main-ring-policy-schedule-timeouts-49f4a8-49f552.o'
OUT = G2 / 'build/c-firmware/20261015/main-system-close-common-data-469d48'
OWNED = {'audio_uart_registry_callback_469d48', 'audio_system_close_selected_20075026',
         'audio_system_close_payload_20074a04'}
RESOLVED = {'audio_uart_registry_callback_469d48'}
ADDED = {'audio_system_close_active_app_get_443504'}
IMPORTS = ADDED | {'audio_log_extended', 'audio_log_flags', 'audio_log_wake_allowed',
                   'audio_system_alert_command_45a8ee', 'audio_uart_device_role_get',
                   'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_SYSTEM_CLOSE_COMMON_DATA_469D48'
            or oracle['cases'] != 768 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('System-close oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'system_close_common_data_469d48.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('System-close object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 188 or before & RESOLVED != RESOLVED or \
            not (IMPORTS - ADDED) <= provided or provided & OWNED:
        raise RuntimeError('System-close base contract changed')
    linked = OUT / 'apollo-main-system-close-common-data-469d48.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before != ADDED or len(after) != 188:
        raise RuntimeError('System-close link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SYSTEM_CLOSE_COMMON_DATA_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': sorted(ADDED), 'unresolved_before': 188, 'unresolved_after': 188,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Active-app getter remains an exposed import; state spans are bounded by observed writes, and final RAM placement remains open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 188, 188, sha(path))

if __name__ == '__main__': main()
