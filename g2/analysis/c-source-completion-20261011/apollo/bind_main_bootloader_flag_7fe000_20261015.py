#!/usr/bin/env python3
"""Bind Apollo OTA bootloader flag to an uninitialized 16-byte mapped page."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_bootloader_flag_7fe000.c'
LINKER = G2 / 'components/audio/uart_thread_source_candidate/display_ble_bootloader_flag_7fe000.ld'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = G2 / 'build/c-firmware/20261015/main-dm-dev-pass-hci-conn-4d29c2/apollo-main-dm-dev-pass-hci-conn-4d29c2.o'
OUT = G2 / 'build/c-firmware/20261015/main-bootloader-flag-7fe000'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
NAME = 'audio_ble_bootloader_flag'

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
    if '000010' not in fields or (address is not None and f'{address:08x}' not in fields):
        raise RuntimeError(f'{name}: extent or address changed')

def main():
    if hashlib.sha256(PAYLOAD.read_bytes()[32:]).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    if '0x007fe000 (NOLOAD)' not in LINKER.read_text():
        raise RuntimeError('OTA flag NOLOAD placement changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_bootloader_flag_7fe000.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if names(obj, '--defined-only') != {NAME} or names(obj, '-u'):
        raise RuntimeError('OTA flag C symbols changed')
    section(obj, '.bss.opencfw.ota.bootloader_flag')
    placed = OUT / 'bootloader-flag-placement.elf'
    subprocess.run(['arm-none-eabi-ld', '-T', str(LINKER), str(obj), '-o', str(placed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    section(placed, '.opencfw.ota.bootloader_flag', 0x7fe000)
    addresses = {line.split()[-1]: int(line.split()[0], 16)
                 for line in output('arm-none-eabi-nm', '-g', '--defined-only', str(placed)).splitlines()}
    if addresses.get(NAME) != 0x7fe000:
        raise RuntimeError('OTA flag symbol is not at native address')
    before = names(BASE, '-u')
    if len(before) != 191 or NAME not in before:
        raise RuntimeError('Main OTA flag import frontier changed')
    linked = OUT / 'apollo-main-bootloader-flag-7fe000.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = names(linked, '-u')
    if len(after) != 190 or before-after != {NAME} or after-before:
        raise RuntimeError('Main OTA flag link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_BOOTLOADER_FLAG_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'linker_fragment': str(LINKER.relative_to(ROOT)), 'linker_sha256': sha(LINKER),
               'payload_sha256': PINNED_SHA,
               'object_sha256': sha(obj), 'placement_elf': str(placed.relative_to(ROOT)),
               'placement_sha256': sha(placed), 'placement_address': '0x007fe000',
               'section_type': 'NOBITS', 'section_bytes': 16,
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': [NAME], 'unresolved_before': 191,
               'unresolved_after': 190, 'imports_resolved': [NAME], 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['This reserves four persistent words without initial contents. Final Main linker integration, flash erase/program behavior, and device persistence are unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
