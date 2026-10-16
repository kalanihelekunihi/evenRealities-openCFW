#!/usr/bin/env python3
"""Bind native positive LTK HCI reply 0x52b2ce to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_hci_ltk_reply_52b2ce.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-hci-ltk-reply-52b2ce'
BASE = G2 / 'build/c-firmware/20261015/main-dm-sec-lesc-neg-ltk/apollo-main-dm-sec-lesc-neg-ltk.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'HciLeLtkReqReplCmd'}
EXISTING = {'audio_ble_hci_cmd_alloc_52ae38', 'audio_ble_hci_cmd_send'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STOCK_SHA = '437472191b978f154caffca5ba1ef11e48d3d6da448a301911659d250242bfa9'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x52b2ce-0x438000:0x52b304-0x438000]).hexdigest() != STOCK_SHA:
        raise RuntimeError('Apollo positive LTK native body changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_HCI_LTK_REPLY_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 12:
        raise RuntimeError('positive LTK oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_hci_ltk_reply_52b2ce.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != EXISTING:
        raise RuntimeError('positive LTK source symbols changed')
    linked = OUT / 'apollo-main-hci-ltk-reply-52b2ce.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 202 or len(after) != 201 or \
            before - after != OWNED or after - before:
        raise RuntimeError('positive LTK link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_HCI_LTK_REPLY_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_body_sha256': STOCK_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['STK getter and SMP encrypt indication remain exposed; controller effects and final placement remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
