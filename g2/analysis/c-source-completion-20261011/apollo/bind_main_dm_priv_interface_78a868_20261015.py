#!/usr/bin/env python3
"""Bind primary Cordio privacy interface and expose six HCI/DM children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_priv_interface_78a868.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-priv-interface-78a868'
BASE = G2 / 'build/c-firmware/20261015/main-mram-records-7ff000/apollo-main-mram-records-7ff000.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_priv_table_a', 'audio_ble_dm_priv_actions',
         'audio_ble_dm_priv_reset_4d27c0', 'audio_ble_dm_priv_hci_handler_4d26e8',
         'audio_ble_dm_priv_msg_handler_4d27ae'}
EXISTING = {'audio_ble_dm_priv_cb_storage', 'audio_ble_dm_handler_state',
            'memcpy', 'memset', 'SecAes', 'SecRand'}
ADDED = {'HciLeAddDeviceToResolvingListCmd', 'HciLeRemoveDeviceFromResolvingList',
         'HciLeClearResolvingList', 'HciLeSetAddrResolutionEnable',
         'HciLeSetPrivacyModeCmd', 'dmDevPassEvtToDevPriv'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SPANS = [(0x78a868, 0x78a874, '0a828f9f2f60975a2bfcd05cfab0165ef8345846053d2eb4e4ae7de5bf5ddb2d'),
         (0x76af6c, 0x76af88, 'cc0a59500ccf4bb1ca931d4ee0a65a3baf810bca499b899fd8d11721364fe12c'),
         (0x4d254c, 0x4d27e0, '7f5e4092084956c3085b4afe1bb9d044936b6bd4277db0538070e08116dbfe7d')]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or any(
            hashlib.sha256(blob[a-0x438000:z-0x438000]).hexdigest() != expected
            for a, z, expected in SPANS):
        raise RuntimeError('Apollo primary privacy native bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_INTERFACE_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 80:
        raise RuntimeError('primary privacy oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_priv_interface_78a868.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if 'audio_ble_dm_priv_table_a' not in before or \
            not EXISTING <= defined or symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING | ADDED:
        raise RuntimeError('primary privacy C symbol set changed')
    linked = OUT / 'apollo-main-dm-priv-interface-78a868.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    resolved = {'audio_ble_dm_priv_table_a'}
    if len(before) != 193 or len(after) != 198 or \
            before-after != resolved or after-before != ADDED:
        raise RuntimeError('primary privacy C link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_INTERFACE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA,
               'stock_spans': [{'begin': hex(a), 'end': hex(z), 'sha256': h}
                               for a, z, h in SPANS],
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(resolved), 'imports_added': sorted(ADDED),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Six native HCI/DM child calls are now exposed as unresolved imports; valid privacy actions and HCI cases have bounded comparisons, not full hardware proof.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
