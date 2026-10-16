#!/usr/bin/env python3
"""Bind native-backed tracepoint master/phone reply router."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_reply_result_5ee134.c'
ORACLE_SCRIPT = G2 / 'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_reply_result_5ee134_20261015.py'
ORACLE = G2 / 'build/c-firmware/20261015/main-tracepoint-reply-result-5ee134/oracle.json'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-tracepoint-reply-buffer-2037bbc8/apollo-main-tracepoint-reply-buffer-2037bbc8.o'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-reply-result-5ee134'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'audio_tracepoint_reply_result_5ee134'}
ADDED = {'audio_tracepoint_send_to_master_5ee066',
         'audio_tracepoint_send_to_phone_5edfd8'}

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
    if oracle['status'] != 'PASS_BOUNDED_MAIN_TRACEPOINT_REPLY_ROUTING_NATIVE_C' or \
            len(oracle['cases']) != 240 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('tracepoint reply-router native/C oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'tracepoint_reply_result_5ee134.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED:
        raise RuntimeError('tracepoint reply-router C provider changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-tracepoint-reply-result-5ee134.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 193 or len(after) != 194 or \
            before-after != OWNED or after-before != ADDED:
        raise RuntimeError('Main tracepoint reply-router import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REPLY_ROUTING_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'native_c_cases': 240, 'payload_sha256': PINNED,
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': 193, 'unresolved_after': 194,
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(ADDED),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The native master and phone send children remain imports.',
                          'Child effects are compared at call boundaries; final placement and hardware execution are unproved.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
