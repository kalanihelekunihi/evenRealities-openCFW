#!/usr/bin/env python3
"""Bind four pinned Cordio privacy HCI command builders to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_hci_privacy_commands_52b744.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-hci-privacy-commands-52b744'
BASE = G2 / 'build/c-firmware/20261015/main-hci-addr-resolution-enable-52b7f6/apollo-main-hci-addr-resolution-enable-52b7f6.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'HciLeAddDeviceToResolvingListCmd', 'HciLeRemoveDeviceFromResolvingList',
         'HciLeClearResolvingList', 'HciLeSetPrivacyModeCmd'}
EXISTING = {'hciCmdAlloc', 'hciCmdSend', 'memcpy'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SPANS = [(0x52b744, 0x52b794, 'c67f36dde4851b188481aa1620b69ff92b9d04a5dc547364dd0e70bb372e36f4'),
         (0x52b794, 0x52b7c2, '3dd9451a3dc29c6c8841436bbb5ada41d853a2b8c807a498d7adf091b476d91f'),
         (0x52b7c2, 0x52b7dc, 'fc500d5cd9c541dd114d37be901e98838ca9e0591ceb686c9460edacd4678ac3'),
         (0x52b818, 0x52b84c, 'eab460e199af9c97d4b13cd76beed0ef0df6aa4c97ac5864a67411378d82568b')]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or any(
            hashlib.sha256(blob[a-0x438000:z-0x438000]).hexdigest() != expected
            for a, z, expected in SPANS):
        raise RuntimeError('Apollo privacy HCI command bytes changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_HCI_PRIVACY_COMMANDS_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 24:
        raise RuntimeError('privacy HCI command oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_hci_privacy_commands_52b744.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != EXISTING:
        raise RuntimeError('privacy HCI command C symbols changed')
    linked = OUT / 'apollo-main-hci-privacy-commands-52b744.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 197 or len(after) != 193 or before-after != OWNED or after-before:
        raise RuntimeError('privacy HCI command link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HCI_PRIVACY_COMMANDS_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA,
               'stock_spans': [{'begin': hex(a), 'end': hex(z), 'sha256': h}
                               for a, z, h in SPANS],
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Command construction is C-bound; HCI transport/controller effects, final placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
