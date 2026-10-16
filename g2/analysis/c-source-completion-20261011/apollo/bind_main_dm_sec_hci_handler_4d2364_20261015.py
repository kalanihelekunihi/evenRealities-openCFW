#!/usr/bin/env python3
"""Bind Cordio security HCI handler 0x4d2364 and expose its five children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_sec_hci_handler_4d2364.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-sec-hci-handler-4d2364'
BASE = G2 / 'build/c-firmware/20261015/main-dm-dispatch-scan-start-536820/apollo-main-dm-dispatch-scan-start-536820.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_dm_dispatch_4d2364'}
NEW = {'HciLeLtkReqNegReplCmd', 'HciLeLtkReqReplCmd',
       'audio_ble_smp_encrypt_ind_537be6', 'audio_ble_smp_get_stk_537c4c',
       'audio_ble_smp_lesc_enabled_537c30'}
EXISTING = {'audio_ble_dm_conn_ccb_by_handle_4b601c', 'g2_lfs_memcmp',
            'DmConnSetIdle', 'DmSmpCbackExec', 'audio_ble_dm_handler_state'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STOCK_SHA = '0487ba4b9d4d93d5d414c875b37afcaf6a9fa2628fa6193fa979f282678a1024'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x4d2364-0x438000:0x4d2440-0x438000]).hexdigest() != STOCK_SHA:
        raise RuntimeError('Apollo DM security HCI native body changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_DM_SEC_HCI_HANDLER_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 256:
        raise RuntimeError('DM security HCI oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_dm_sec_hci_handler_4d2364.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or \
            symbols(obj, '-u') != EXISTING | NEW or NEW & (before | defined):
        raise RuntimeError('DM security HCI source symbols changed')
    linked = OUT / 'apollo-main-dm-sec-hci-handler-4d2364.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 200 or len(after) != 204 or \
            before - after != OWNED or after - before != NEW:
        raise RuntimeError('DM security HCI link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_SEC_HCI_HANDLER_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_body_sha256': STOCK_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': sorted(NEW),
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Five exposed SMP and LTK HCI children require separate C bodies.',
                          'Failure-event native stack padding is not initialized; final RAM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
