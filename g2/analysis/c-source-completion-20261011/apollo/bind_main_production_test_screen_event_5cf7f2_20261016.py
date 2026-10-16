#!/usr/bin/env python3
"""Bind stock-checked production-test screen callback to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/production_test_screen_event_5cf7f2.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-production-test-screen-event-5cf7f2/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-system-close-active-app-get-443504/apollo-main-system-close-active-app-get-443504.o'
OUT = G2 / 'build/c-firmware/20261015/main-production-test-screen-event-5cf7f2'
OWNED = {'audio_uart_registry_callback_5cf7f2', 'audio_uart_production_test_root_20074894'}
RESOLVED = {'audio_uart_registry_callback_5cf7f2'}
ADDED = {'audio_uart_page_441068'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_PRODUCTION_TEST_SCREEN_EVENT_5CF7F2' or \
            oracle['cases'] != 28 or oracle['source_sha256'] != sha(SOURCE) or \
            oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
        raise RuntimeError('production-test screen oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'production_test_screen_event_5cf7f2.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED:
        raise RuntimeError('production-test screen source ownership changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 187 or not RESOLVED <= before or \
            symbols(obj, '-u') - before - provided != ADDED:
        raise RuntimeError('production-test screen base frontier changed')
    linked = OUT / 'apollo-main-production-test-screen-event-5cf7f2.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before != ADDED or len(after) != 187:
        raise RuntimeError('production-test screen link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_PRODUCTION_TEST_SCREEN_EVENT_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': sorted(ADDED), 'unresolved_before': 187, 'unresolved_after': 187,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['UI call targets and two RAM writes were controlled; registry context final placement remains open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 187, 187, sha(path))
if __name__ == '__main__': main()
