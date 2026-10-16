#!/usr/bin/env python3
"""Bind the stock-compared EvenAI common-data handler into Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/even_ai_common_data_4e2976.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-even-ai-common-4e2976/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261016/main-align-to-bound/apollo-main-align-to-bound.o'
OUT = G2 / 'build/c-firmware/20261016/main-even-ai-common-bound'
ADDED = {'audio_even_ai_prepare_4e1f7c', 'audio_even_ai_frame_process_4e31cc',
         'audio_even_ai_local_decode_498092', 'audio_even_ai_ready_4e20f2'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_NATIVE_MAIN_EVEN_AI_COMMON_4E2976' or \
            oracle['cases'] != 90 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('EvenAI common-data stock comparison changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'even_ai_common_data_4e2976.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != {'audio_uart_registry_callback_4e2976'}:
        raise RuntimeError('EvenAI common-data source ownership changed')
    before = symbols(BASE, '-u')
    if len(before) != 181 or 'audio_uart_registry_callback_4e2976' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-even-ai-common-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != {'audio_uart_registry_callback_4e2976'} or \
            after - before != ADDED or len(after) != 184:
        raise RuntimeError('Apollo main EvenAI common-data frontier changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_EVEN_AI_COMMON_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
        'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'source_owned_symbols': ['audio_uart_registry_callback_4e2976'],
        'unresolved_before': 181, 'unresolved_after': 184,
        'imports_resolved': ['audio_uart_registry_callback_4e2976'],
        'imports_added': sorted(ADDED),
        'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['Four lower EvenAI functions remain external.',
                   'Stock comparisons cover two supported kinds and the rejection kind with controlled lower calls.',
                   'Final code and RAM placement and physical execution remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
