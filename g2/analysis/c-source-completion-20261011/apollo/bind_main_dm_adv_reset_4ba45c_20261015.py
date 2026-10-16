#!/usr/bin/env python3
"""Bind native Cordio legacy advertising reset to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_adv_reset_4ba45c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-adv-reset-4ba45c'
BASE = G2 / 'build/c-firmware/20261015/main-dm-dev-priv-forward-4b2ea6/apollo-main-dm-dev-priv-forward-4b2ea6.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_adv_reset_4ba45c'}
EXISTING = {'WsfTimerStop', 'audio_ble_dm_adv_control',
            'audio_ble_dm_adv_lower', 'audio_ble_dm_handler_state'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STOCK_SHA = '5c30215302bedc9322e389ee8f3d26f4e120239a391a590e663f9a49b067cff2'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x4ba45c-0x438000:0x4ba490-0x438000]).hexdigest() != STOCK_SHA:
        raise RuntimeError('Apollo advertising reset bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_ADV_RESET_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 24:
        raise RuntimeError('advertising reset oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_adv_reset_4ba45c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if OWNED & (before | defined) or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != EXISTING:
        raise RuntimeError('advertising reset C symbols changed')
    linked = OUT / 'apollo-main-dm-adv-reset-4ba45c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 192 or len(after) != 192 or before != after:
        raise RuntimeError('advertising reset link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_ADV_RESET_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_span_sha256': STOCK_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': [], 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['The advertising reset body is C-owned; the interface HCI and message handlers, action table, final placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
