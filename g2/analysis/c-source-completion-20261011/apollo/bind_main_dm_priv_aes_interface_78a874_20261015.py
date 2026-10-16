#!/usr/bin/env python3
"""Bind Cordio privacy AES interface, action table and control block to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_priv_aes_interface_78a874.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-priv-aes-interface-78a874'
BASE = G2 / 'build/c-firmware/20261015/main-dm-lesc-interface-78a8a4/apollo-main-dm-lesc-interface-78a8a4.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_priv_table_b', 'audio_ble_dm_priv_aes_actions',
         'audio_ble_dm_priv_aes_msg_handler_4d27ce', 'audio_ble_dm_priv_cb_storage'}
EXISTING = {'audio_ble_dm_empty_reset_4d29be', 'audio_ble_dm_empty_handler_4d29c0',
            'audio_ble_dm_handler_state', 'memcmp', 'memcpy'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SPANS = [(0x4d27ce, 0x4d27e0, 'a2031e99f1faff651aa9478f2d8647e5cc2b6b69fb5c381185c365ee9b3ca008'),
         (0x4d25ba, 0x4d25f2, 'edb50d8f35f4f656f3e05595ac05c7355233cd3a2446cd12198a6623a2c832b2'),
         (0x4d26ac, 0x4d26e8, '4a082cbd709d25c36f6fb0849e72afa2dd7937e0fe0c39adea52a2b186c1db30'),
         (0x78a874, 0x78a880, '92413ce5091a3431cfd9a81ad3214a19228dae374292f6a84a063c79c00d809a'),
         (0x78d454, 0x78d45c, '0b4418241c4a15ed8eb3f5cdca2585b5cd114465eaa91ca5e0933e9c7f1799ba')]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or any(
            hashlib.sha256(blob[a-0x438000:z-0x438000]).hexdigest() != expected
            for a, z, expected in SPANS):
        raise RuntimeError('Apollo DM privacy AES native bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_AES_INTERFACE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 12:
        raise RuntimeError('DM privacy AES oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_priv_aes_interface_78a874.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_priv_table_b' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING:
        raise RuntimeError('DM privacy AES source symbols changed')
    linked = OUT / 'apollo-main-dm-priv-aes-interface-78a874.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_priv_table_b'}
    if len(before) != 196 or len(after) != 195 or \
            before - after != resolved or after - before:
        raise RuntimeError('DM privacy AES link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_AES_INTERFACE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA,
               'stock_spans': [{'begin': hex(a), 'end': hex(z), 'sha256': h}
                               for a, z, h in SPANS],
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Only two valid privacy AES action indices are compared; native RAM placement and whole-image behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
