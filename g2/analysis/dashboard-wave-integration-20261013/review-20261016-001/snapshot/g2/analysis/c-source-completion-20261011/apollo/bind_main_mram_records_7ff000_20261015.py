#!/usr/bin/env python3
"""Bind the two Apollo mapped-MRAM names to one NOLOAD C reservation."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_mram_records_7ff000.c'
LINKER = G2 / 'components/audio/uart_thread_source_candidate/display_ble_mram_records_7ff000.ld'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-mram-records-7ff000'
BASE = G2 / 'build/c-firmware/20261015/main-dm-priv-aes-interface-78a874/apollo-main-dm-priv-aes-interface-78a874.o'
OWNED = {'audio_ble_mram_records_7ff000', 'audio_ble_privacy_nvm_records'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def output(*args): return subprocess.check_output(args, text=True)
def names(path, flag):
    return {line.split()[-1] for line in output('arm-none-eabi-nm', '-g', flag, str(path)).splitlines()}
def section(path, name, size, address=None):
    lines = output('arm-none-eabi-readelf', '-SW', str(path)).splitlines()
    matches = [x for x in lines if re.search(r'\s' + re.escape(name) + r'\s+NOBITS\s+', x)]
    if len(matches) != 1:
        raise RuntimeError(f'{name} must be one NOBITS section')
    fields = matches[0].split()
    if f'{size:06x}' not in fields or (address is not None and f'{address:08x}' not in fields):
        raise RuntimeError(f'{name} extent or address changed')

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    if 'audio_ble_mram_records_7ff000' not in SOURCE.read_text() or \
            '0x007ff000 (NOLOAD)' not in LINKER.read_text():
        raise RuntimeError('MRAM C source or NOLOAD placement changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_mram_records_7ff000.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != OWNED or names(obj, '-u'):
        raise RuntimeError('MRAM C symbols changed')
    section(obj, '.bss.opencfw.mram.records', 2560)
    placed = OUT / 'mram-records-placement.elf'
    subprocess.run(['arm-none-eabi-ld', '-T', str(LINKER), str(obj), '-o', str(placed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    section(placed, '.opencfw.mram.records', 2560, 0x7ff000)
    placed_names = {line.split()[-1]: int(line.split()[0], 16)
                    for line in output('arm-none-eabi-nm', '-g', '--defined-only', str(placed)).splitlines()}
    if {placed_names.get(name) for name in OWNED} != {0x7ff000}:
        raise RuntimeError('MRAM aliases do not share native address')
    before = names(BASE, '-u')
    if not OWNED <= before:
        raise RuntimeError('MRAM imports no longer present in Main')
    linked = OUT / 'apollo-main-mram-records-7ff000.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(before) != 195 or len(after) != 193 or before-after != OWNED or after-before:
        raise RuntimeError('Main mapped-MRAM link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_MRAM_RECORDS_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'linker_fragment': str(LINKER.relative_to(ROOT)), 'linker_sha256': sha(LINKER),
               'payload_sha256': PINNED_SHA,
               'object_sha256': sha(obj), 'placement_elf': str(placed.relative_to(ROOT)),
               'placement_sha256': sha(placed), 'placement_address': '0x007ff000',
               'section_type': 'NOBITS', 'section_bytes': 2560,
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'unresolved_before': len(before),
               'unresolved_after': len(after), 'imports_resolved': sorted(OWNED),
               'imports_added': [], 'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The object reserves persistent mapped MRAM without initial contents; final Main linker integration and device persistence are unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
