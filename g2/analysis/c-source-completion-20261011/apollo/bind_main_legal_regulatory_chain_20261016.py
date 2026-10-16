#!/usr/bin/env python3
"""Bind native-checked legal UI callback, fade action, helpers and root cell."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE_DIR = G2 / 'components/audio/uart_thread_source_candidate'
SOURCES = tuple(SOURCE_DIR / name for name in (
    'legal_regulatory_event_5bf7b8.c',
    'legal_regulatory_fade_in_58c238.c',
    'legal_regulatory_fade_helpers.c',
    'legal_regulatory_root_cell.c',
))
BASE = G2 / 'build/c-firmware/20261016/main-distortion-screen-closure/apollo-main-distortion-screen-closure.o'
ORACLES = (
    (G2 / 'build/c-firmware/20261016/main-legal-regulatory-event-5bf7b8/oracle-receipt.json',
     'PASS_NATIVE_MAIN_LEGAL_REGULATORY_EVENT_5BF7B8', 140),
    (G2 / 'build/c-firmware/20261016/main-legal-fade-in-58c238/oracle-receipt.json',
     'PASS_NATIVE_MAIN_LEGAL_FADE_IN_58C238', 300),
    (G2 / 'build/c-firmware/20261016/main-legal-fade-helpers/oracle-receipt.json',
     'PASS_NATIVE_MAIN_LEGAL_FADE_HELPERS', 64),
)
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OUT = G2 / 'build/c-firmware/20261016/main-legal-regulatory-chain'
OWNED = {'audio_uart_registry_callback_5bf7b8', 'audio_uart_page_58c238',
         'audio_legal_regulatory_fade_callback_58c12c',
         'audio_uart_lv_anim_path_45065a',
         'audio_legal_regulatory_root_200746a4'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('stock payload changed')
    literals = {}
    for address, expected in ((0x5bf8a4, 0x200746a4),
                              (0x5bf958, 0x200014cc),
                              (0x58c74c, 0x58c12d),
                              (0x58c750, 0x45065b)):
        value = struct.unpack_from('<I', image, address - 0x438000)[0]
        if value != expected:
            raise RuntimeError(f'legal callback pointer at {address:x} changed')
        literals[f'0x{address:06x}'] = f'0x{value:08x}'
    oracle_refs = []
    for path, status, cases in ORACLES:
        data = json.loads(path.read_text())
        if data['status'] != status or data['cases'] != cases or \
                data['official_payload_sha256'] != PAYLOAD_SHA or \
                data['source_sha256'] != sha(ROOT / data['source']):
            raise RuntimeError(f'legal oracle changed: {path}')
        oracle_refs.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                            'status': status, 'cases': cases})
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for source in SOURCES:
        obj = OUT / (source.stem + '.o')
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)], check=True)
        objects.append(obj)
    defined = set().union(*(symbols(obj, '--defined-only') for obj in objects))
    if defined != OWNED:
        raise RuntimeError(f'legal source ownership changed: {defined ^ OWNED}')
    root_nm = subprocess.check_output(['arm-none-eabi-nm', '-S', str(objects[3])], text=True)
    if '00000000 00000004 B audio_legal_regulatory_root_200746a4' not in root_nm:
        raise RuntimeError('observed legal root word changed')
    before = symbols(BASE, '-u')
    if len(before) != 182 or 'audio_uart_registry_callback_5bf7b8' not in before:
        raise RuntimeError('Apollo main base frontier changed')
    linked = OUT / 'apollo-main-legal-regulatory-chain.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), *(str(o) for o in objects),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_uart_registry_callback_5bf7b8'}
    added = {'audio_legal_regulatory_build_5bf332'}
    if before - after != resolved or after - before != added or len(after) != 182:
        raise RuntimeError('Apollo main legal callback link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_LEGAL_REGULATORY_CHAIN_C',
               'source_files': [{'path': str(s.relative_to(ROOT)), 'sha256': sha(s)} for s in SOURCES],
               'official_payload_sha256': PAYLOAD_SHA, 'stock_pointer_literals': literals,
               'oracles': oracle_refs,
               'source_owned_symbols': sorted(OWNED),
               'objects': [{'path': str(o.relative_to(ROOT)), 'sha256': sha(o)} for o in objects],
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': 182, 'unresolved_after': 182,
               'imports_resolved': sorted(resolved), 'imports_added': sorted(added),
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['The legal page builder 0x5bf332 remains an unresolved C provider.',
                          'The root cell is an observed four-byte reservation, not final RAM placement.',
                          'Page, animation, logging and scroll children are controlled in the bounded oracles.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 182, 182, sha(path))

if __name__ == '__main__': main()
