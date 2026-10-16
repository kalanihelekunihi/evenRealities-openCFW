#!/usr/bin/env python3
"""Verify stock DM dispatch slots and the C interface alias."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_stack_interface_78a88c.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_main.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-stack-interface-78a88c'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_dispatch_536820', 0x536821),
         ('audio_ble_dm_dispatch_536896', 0x536897),
         ('audio_ble_dm_dispatch_5368ae', 0x5368af),
         ('audio_ble_dm_stack_reset_536918', 0x536919),
         ('audio_ble_dm_stack_hci_handler_53694c', 0x53694d),
         ('audio_ble_dm_stack_msg_handler_5369d8', 0x5369d9),
         ('audio_ble_dm_dispatch_4d2544', 0x4d2545),
         ('audio_ble_dm_dispatch_4d2364', 0x4d2365)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    offset = 0x78a880 - 0x438000
    actual = [int.from_bytes(blob[offset+i*4:offset+i*4+4], 'little')
              for i in range(8)]
    if actual != [value for _, value in SLOTS]:
        raise RuntimeError('native DM interface pointer slots changed')
    upstream = UPSTREAM.read_text()
    if 'dmFcnIf_t *dmFcnIfTbl[DM_NUM_IDS]' not in upstream or \
            'dmFcnDefault' not in upstream:
        raise RuntimeError('Cordio interface source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_stack_interface_78a88c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE),
                    '-o', str(obj)], check=True)
    table = subprocess.check_output(['arm-none-eabi-readelf', '-sW', str(obj)], text=True)
    base = re.search(r'^\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+OBJECT\s+GLOBAL\s+DEFAULT\s+(\d+)\s+audio_ble_dm_dispatch_table_78a880$', table, re.M)
    alias = re.search(r'^\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+OBJECT\s+GLOBAL\s+DEFAULT\s+(\d+)\s+audio_ble_dm_stack_table_78a88c$', table, re.M)
    if base is None or alias is None or int(base.group(2)) != 32 or \
            int(alias.group(2)) != 20 or base.group(3) != alias.group(3) or \
            int(alias.group(1), 16) - int(base.group(1), 16) != 12:
        raise RuntimeError('compiled DM dispatch table and interface alias changed')
    reloc = subprocess.check_output(['arm-none-eabi-objdump', '-r', str(obj)], text=True)
    found = re.findall(r'^([0-9a-f]{8})\s+R_ARM_ABS32\s+(audio_ble_dm_(?:stack|dispatch)_\w+)$', reloc, re.M)
    expected = [(f'{i*4:08x}', name) for i, (name, _) in enumerate(SLOTS)]
    if found != expected:
        raise RuntimeError(f'DM interface pointer relocation order changed: {found}')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_STACK_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'object_sha256': sha(obj), 'record_bytes': 32,
               'stack_interface_alias_offset': 12,
               'stock_thumb_pointers': [hex(value) for _, value in SLOTS],
               'symbolic_relocations': expected,
               'limits': ['The eight child bodies are unresolved; native pointer values establish slot identity, not final C placement or execution.',
                          'The stack interface at 0x78a88c aliases slot three of the 0x78a880 dispatch table.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], sha(path))

if __name__ == '__main__': main()
