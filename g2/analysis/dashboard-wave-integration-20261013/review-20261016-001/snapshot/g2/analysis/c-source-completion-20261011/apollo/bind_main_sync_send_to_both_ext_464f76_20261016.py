#!/usr/bin/env python3
"""Bind stock-checked SendDataToBothExt packet and queue path."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/sync_send_to_both_ext_464f76.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-sync-send-to-both-ext-464f76/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-silent-mode-set-from-app-46921c/apollo-main-silent-mode-set-from-app-46921c.o'
OUT = G2 / 'build/c-firmware/20261015/main-sync-send-to-both-ext-464f76'
OWNED = {'audio_sync_send_to_both_ext_464f76'}
IMPORTS = {'audio_cmsis_queue_put', 'audio_file_heap_free', 'audio_log_extended',
           'audio_log_flags', 'audio_queue_copy_bytes', 'audio_uart_alloc_retry',
           'audio_uart_buffer_zero', 'compressed_log_output',
           'g2_log_event_set_task', 'g2_uart_send_queue', 'g2_uart_thread_event'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_SYNC_SEND_TO_BOTH_EXT_464F76'
            or oracle['cases'] != 500 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Send-to-both evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'sync_send_to_both_ext_464f76.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Send-to-both object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 190 or before & OWNED != OWNED or not IMPORTS <= provided:
        raise RuntimeError('Send-to-both base contract changed')
    linked = OUT / 'apollo-main-sync-send-to-both-ext-464f76.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 189:
        raise RuntimeError('Send-to-both link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SYNC_SEND_TO_BOTH_EXT_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 190, 'unresolved_after': 189,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Heap allocation, queue and event operations remain bounded controlled calls; final transport integration and hardware behavior remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 190, 189, sha(path))

if __name__ == '__main__': main()
