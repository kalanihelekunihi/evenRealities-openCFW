#!/usr/bin/env python3
"""Bind pinned four-byte Apollo registration assertion context."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_audio_registration_assert_context_45f678.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-registration-assert-context-45f678'
BASE = G2 / 'build/c-firmware/20261015/main-audio-enqueue-alloc-failure-45f402/apollo-main-audio-enqueue-alloc-failure-45f402.o'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OWNED = {'g2_audio_page_registration_template_45f678'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stock = PAYLOAD.read_bytes()[32 + 0x45f678 - 0x438000:][:4]
    if stock != b'0\x00\x00\x00':
        raise RuntimeError('Apollo assertion context bytes changed')
    obj = OUT / 'display_audio_registration_assert_context_45f678.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    if not OWNED <= before or symbols(obj, '--defined-only') != OWNED:
        raise RuntimeError('Apollo assertion context symbol changed')
    linked = OUT / 'apollo-main-audio-registration-assert-context-45f678.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 209 or len(after) != 208 or \
            before - after != OWNED or after - before:
        raise RuntimeError('Apollo assertion context link changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ASSERT_CONTEXT_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'stock_address': '0x45f678',
               'stock_bytes': stock.hex(), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Four source-owned bytes match the pinned payload.',
                          'Final ROM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
