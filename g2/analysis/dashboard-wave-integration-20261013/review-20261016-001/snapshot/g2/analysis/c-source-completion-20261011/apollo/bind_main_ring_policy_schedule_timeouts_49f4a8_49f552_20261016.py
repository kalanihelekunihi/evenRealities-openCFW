#!/usr/bin/env python3
"""Bind stock-checked ring connect and reconnect timeout schedulers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ring_policy_schedule_timeouts_49f4a8_49f552.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-ring-policy-schedule-timeouts-49f4a8-49f552/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-ring-policy-cancel-connect-timeout-49f5f8/apollo-main-ring-policy-cancel-connect-timeout-49f5f8.o'
OUT = G2 / 'build/c-firmware/20261015/main-ring-policy-schedule-timeouts-49f4a8-49f552'
OWNED = {'audio_ble_ring_policy_schedule_connect_timeout_49f4a8',
         'audio_ble_ring_policy_schedule_reconnect_timeout_49f552'}
IMPORTS = {'audio_ble_master_success_delayed', 'audio_ble_ring_policy_delayed',
           'audio_ble_ring_policy_pending_2007500b',
           'audio_event_loop_push_delayed', 'audio_event_loop_remove_delayed',
           'audio_log_extended', 'audio_log_flags', 'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_RING_POLICY_SCHEDULE_TIMEOUTS_49F4A8_49F552'
            or oracle['cases'] != 36 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Ring timeout scheduling oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'ring_policy_schedule_timeouts_49f4a8_49f552.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Ring timeout scheduling object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 190 or before & OWNED != OWNED or not IMPORTS <= provided:
        raise RuntimeError('Ring timeout scheduling base contract changed')
    linked = OUT / 'apollo-main-ring-policy-schedule-timeouts-49f4a8-49f552.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 188:
        raise RuntimeError('Ring timeout scheduling link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_RING_POLICY_SCHEDULE_TIMEOUTS_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 190, 'unresolved_after': 188,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Event scheduling uses preexisting C providers; final scheduler timing and hardware execution remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 190, 188, sha(path))

if __name__ == '__main__': main()
