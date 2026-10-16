#!/usr/bin/env python3
"""Bind only the observed eight-byte minimum of two UI test contexts."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/test_screen_registry_context_min.c'
BASE = G2 / 'build/c-firmware/20261015/main-gray-screen-event-5cf67e/apollo-main-gray-screen-event-5cf67e.o'
OUT = G2 / 'build/c-firmware/20261015/main-test-screen-registry-context-min'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
OWNED = {'audio_uart_registry_context_20003080', 'audio_uart_registry_context_200030a0'}
GRAY_ORACLE = G2 / 'build/c-firmware/20261016/main-gray-screen-event-5cf67e/oracle-receipt.json'
PRODUCTION_ORACLE = G2 / 'build/c-firmware/20261016/main-production-test-screen-event-5cf7f2/oracle-receipt.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    if hashlib.sha256(IMAGE).hexdigest() != IMAGE_SHA:
        raise RuntimeError('stock payload changed')
    rows = []
    for address, expected in ((0x6a45d0, (0x10f, 0x5cf635, 0x5cf67f, 0x20003080)),
                              (0x6a45e0, (0x10b, 0x5cf7a9, 0x5cf7f3, 0x200030a0))):
        values = struct.unpack_from('<4I', IMAGE, address - 0x438000)
        if values != expected: raise RuntimeError('stock UI test registry row changed')
        rows.append({'address': f'0x{address:08x}', 'words': [f'0x{x:08x}' for x in values],
                     'sha256': hashlib.sha256(IMAGE[address - 0x438000:
                                                     address - 0x438000 + 16]).hexdigest()})
    for path, status in ((GRAY_ORACLE, 'PASS_NATIVE_MAIN_GRAY_SCREEN_EVENT_5CF67E'),
                         (PRODUCTION_ORACLE, 'PASS_NATIVE_MAIN_PRODUCTION_TEST_SCREEN_EVENT_5CF7F2')):
        data = json.loads(path.read_text())
        if data['status'] != status or data['cases'] != 28 or \
                data['official_payload_sha256'] != IMAGE_SHA:
            raise RuntimeError('test-screen native state comparison changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'test_screen_registry_context_min.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u'):
        raise RuntimeError('bounded UI context object contract changed')
    sizes = {}
    for line in subprocess.check_output(['arm-none-eabi-nm', '-S', '-g', str(obj)], text=True).splitlines():
        parts = line.split()
        if parts[-1] in OWNED:
            sizes[parts[-1]] = (int(parts[1], 16), parts[2])
    if sizes != {name: (8, 'B') for name in OWNED}:
        raise RuntimeError('bounded UI context sizes changed')
    before = symbols(BASE, '-u')
    if len(before) != 185 or not OWNED <= before:
        raise RuntimeError('bounded UI context base frontier changed')
    linked = OUT / 'apollo-main-test-screen-registry-context-min.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before or len(after) != 183:
        raise RuntimeError('bounded UI context link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_TEST_SCREEN_REGISTRY_CONTEXT_MIN_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'official_payload_sha256': IMAGE_SHA, 'stock_rows': rows,
               'gray_oracle': str(GRAY_ORACLE.relative_to(ROOT)), 'gray_oracle_sha256': sha(GRAY_ORACLE),
               'production_oracle': str(PRODUCTION_ORACLE.relative_to(ROOT)),
               'production_oracle_sha256': sha(PRODUCTION_ORACLE),
               'observed_minimum_bytes_per_context': 8,
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'unresolved_before': 185, 'unresolved_after': 183,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Eight bytes per context cover only the observed +4 root write; full allocation extent, initialization and final RAM placement remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 185, 183, sha(path))
if __name__ == '__main__': main()
