#!/usr/bin/env python3
"""Bind stock-checked legal page builder and helper bodies to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE_DIR = G2 / 'components/audio/uart_thread_source_candidate'
SOURCES = (SOURCE_DIR / 'legal_regulatory_page_helpers.c',
           SOURCE_DIR / 'legal_regulatory_page_build_5bf332.c')
BASE = G2 / 'build/c-firmware/20261016/main-legal-assets-bound/apollo-main-legal-assets-bound.o'
HELPER_ORACLE = G2 / 'build/c-firmware/20261016/main-legal-page-helpers/oracle-receipt.json'
BUILDER_ORACLE = G2 / 'build/c-firmware/20261016/main-legal-page-build-5bf332/oracle-receipt.json'
ASSET_RECEIPT = G2 / 'build/c-firmware/20261016/main-legal-assets/receipt.json'
OUT = G2 / 'build/c-firmware/20261016/main-legal-page-builder-bound'
OWNED = {'audio_uart_page_4413be', 'audio_uart_page_4413ce',
         'audio_uart_page_44144c', 'audio_legal_regulatory_zero_styles_5bf114',
         'audio_legal_regulatory_panel_5bf24e',
         'audio_legal_regulatory_label_5bf298',
         'audio_legal_regulatory_icon_5bf2f8',
         'audio_legal_regulatory_build_5bf332'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    for path, status, cases, source in (
        (HELPER_ORACLE, 'PASS_NATIVE_MAIN_LEGAL_PAGE_HELPERS', 112, SOURCES[0]),
        (BUILDER_ORACLE, 'PASS_NATIVE_MAIN_LEGAL_PAGE_BUILD_5BF332', 3, SOURCES[1]),
    ):
        oracle = json.loads(path.read_text())
        if oracle['status'] != status or oracle['cases'] != cases or \
                oracle['source_sha256'] != sha(source):
            raise RuntimeError(f'legal page oracle changed: {path}')
    builder = json.loads(BUILDER_ORACLE.read_text())
    assets = json.loads(ASSET_RECEIPT.read_text())
    if builder['controlled_lower_calls'] != 333 or \
            builder['visited_stock_instruction_addresses'] != 446 or \
            assets['status'] != 'PASS_SOURCE_OWNED_MAIN_LEGAL_ASSETS' or \
            assets['rows'] != 38 or assets['pixel_bytes'] != 40596:
        raise RuntimeError('legal page builder or resource evidence changed')
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
        raise RuntimeError(f'legal page builder source ownership changed: {defined ^ OWNED}')
    before = symbols(BASE, '-u')
    if len(before) != 182 or 'audio_legal_regulatory_build_5bf332' not in before:
        raise RuntimeError('Apollo main legal asset base frontier changed')
    linked = OUT / 'apollo-main-legal-page-builder-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), *(str(o) for o in objects),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_legal_regulatory_build_5bf332'}
    added = {'audio_uart_page_43f6d6'}
    if before - after != resolved or after - before != added or len(after) != 182:
        raise RuntimeError('Apollo main legal page builder frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_LEGAL_PAGE_BUILDER_C',
               'source_files': [{'path': str(s.relative_to(ROOT)), 'sha256': sha(s)} for s in SOURCES],
               'helper_oracle': str(HELPER_ORACLE.relative_to(ROOT)),
               'helper_oracle_sha256': sha(HELPER_ORACLE),
               'builder_oracle': str(BUILDER_ORACLE.relative_to(ROOT)),
               'builder_oracle_sha256': sha(BUILDER_ORACLE),
               'asset_receipt': str(ASSET_RECEIPT.relative_to(ROOT)),
               'asset_receipt_sha256': sha(ASSET_RECEIPT),
               'source_owned_symbols': sorted(OWNED),
               'objects': [{'path': str(o.relative_to(ROOT)), 'sha256': sha(o)} for o in objects],
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': 182, 'unresolved_after': 182,
               'imports_resolved': sorted(resolved), 'imports_added': sorted(added),
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['The native 0x43f6d6 alignment implementation is not source-owned and remains an import.',
                          'Lower page calls are controlled in the builder oracle; resource bytes are verified separately.',
                          'Final RAM, code/data placement and hardware display behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 182, 182, sha(path))

if __name__ == '__main__': main()
