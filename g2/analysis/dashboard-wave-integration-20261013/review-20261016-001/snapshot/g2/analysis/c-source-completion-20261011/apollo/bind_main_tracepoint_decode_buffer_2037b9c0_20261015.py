#!/usr/bin/env python3
"""Bind the observed 0x206-byte tracepoint decode RAM span."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_decode_buffer_2037b9c0.c'
LINKER = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_decode_buffer_2037b9c0.ld'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
ORACLE = G2 / 'build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc/oracle.json'
BASE = G2 / 'build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc/apollo-main-tracepoint-ble-data-5ee8bc.o'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-decode-buffer-2037b9c0'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NAME = 'audio_tracepoint_decode_buffer'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def output(*args): return subprocess.check_output(args, text=True)
def names(path, flag):
    return {line.split()[-1] for line in output('arm-none-eabi-nm', '-g', flag, str(path)).splitlines()}
def section(path, name, address=None):
    matches = [line for line in output('arm-none-eabi-readelf', '-SW', str(path)).splitlines()
               if re.search(r'\s' + re.escape(name) + r'\s+NOBITS\s+', line)]
    if len(matches) != 1:
        raise RuntimeError(f'{name}: expected one NOBITS section')
    fields = matches[0].split()
    if '000206' not in fields or (address is not None and f'{address:08x}' not in fields):
        raise RuntimeError(f'{name}: extent or address changed')

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED:
        raise RuntimeError('Apollo payload changed')
    needle = (0x2037b9c0).to_bytes(4, 'little')
    positions = [i for i in range(len(blob)) if blob.startswith(needle, i)]
    if positions != [0x5ef020-0x438000]:
        raise RuntimeError('tracepoint decode RAM references changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_BOUNDED_MAIN_TRACEPOINT_BLE_DATA_NATIVE_C' or \
            len(oracle['cases']) != 280 or \
            not any(case['calls'] > 0 for case in oracle['cases']):
        raise RuntimeError('tracepoint decode call evidence changed')
    if '0x2037b9c0 (NOLOAD)' not in LINKER.read_text():
        raise RuntimeError('tracepoint NOLOAD placement changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'tracepoint_decode_buffer_2037b9c0.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != {NAME} or names(obj, '-u'):
        raise RuntimeError('tracepoint RAM source symbols changed')
    section(obj, '.bss.opencfw.tracepoint.decode')
    placed = OUT / 'tracepoint-decode-placement.elf'
    subprocess.run(['arm-none-eabi-ld', '-T', str(LINKER), str(obj), '-o', str(placed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    section(placed, '.opencfw.tracepoint.decode', 0x2037b9c0)
    addresses = {line.split()[-1]: int(line.split()[0], 16)
                 for line in output('arm-none-eabi-nm', '-g', '--defined-only', str(placed)).splitlines()}
    if addresses.get(NAME) != 0x2037b9c0:
        raise RuntimeError('tracepoint RAM symbol address changed')
    before = names(BASE, '-u')
    linked = OUT / 'apollo-main-tracepoint-decode-buffer-2037b9c0.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 193 or len(after) != 192 or \
            before-after != {NAME} or after-before:
        raise RuntimeError('Main tracepoint RAM import frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DECODE_RAM_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'linker_fragment': str(LINKER.relative_to(ROOT)),
               'linker_sha256': sha(LINKER), 'payload_sha256': PINNED,
               'object_sha256': sha(obj), 'placement_elf': str(placed.relative_to(ROOT)),
               'placement_sha256': sha(placed), 'placement_address': '0x2037b9c0',
               'section_type': 'NOBITS', 'section_bytes': 0x206,
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': [NAME], 'unresolved_before': 193,
               'unresolved_after': 192, 'imports_resolved': [NAME], 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['This reserves the observed 0x206-byte clear span, not a proved full allocation extent.',
                          'Final whole-image RAM layout, startup and device behavior are unproved.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
