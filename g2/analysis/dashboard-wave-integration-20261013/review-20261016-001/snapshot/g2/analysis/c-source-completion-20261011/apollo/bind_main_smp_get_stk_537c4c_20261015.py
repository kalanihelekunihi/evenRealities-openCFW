#!/usr/bin/env python3
"""Bind native SmpDmGetStk 0x537c4c and SC level selection to C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_smp_get_stk_537c4c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-smp-get-stk-537c4c'
BASE = G2 / 'build/c-firmware/20261015/main-smp-encrypt-ind-537be6/apollo-main-smp-encrypt-ind-537be6.o'
ORACLE = OUT / 'oracle-receipt.json'
OWNED = {'audio_ble_smp_get_stk_537c4c'}
EXISTING = {'smpCcbByConnId', 'audio_ble_smp_handler_state'}
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STOCK_SHA = 'b21687106d28c1fc6429dd9d0a2afc538f2bc8277439a62eb4adefcfe047cf8f'
LEVEL_SHA = '61dd303ee69a0455daed09e52d75fd9df77550a7c2db6bfa96ee6c988376598d'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            hashlib.sha256(blob[0x537c4c-0x438000:0x537cb2-0x438000]).hexdigest() != STOCK_SHA or \
            hashlib.sha256(blob[0x537c00-0x438000:0x537c30-0x438000]).hexdigest() != LEVEL_SHA:
        raise RuntimeError('Apollo SMP STK native bodies changed')
    oracle = json.loads(ORACLE.read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_SMP_GET_STK_ORACLE' or \
            oracle['source_sha256'] != sha(SOURCE) or oracle['cases'] != 384:
        raise RuntimeError('SMP STK oracle changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_ble_smp_get_stk_537c4c.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if not OWNED <= before or not EXISTING <= defined or \
            symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != EXISTING:
        raise RuntimeError('SMP STK source symbols changed')
    linked = OUT / 'apollo-main-smp-get-stk-537c4c.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 200 or len(after) != 199 or \
            before - after != OWNED or after - before:
        raise RuntimeError('SMP STK link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_SMP_GET_STK_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_body_sha256': STOCK_SHA,
               'stock_sc_level_sha256': LEVEL_SHA,
               'oracle_receipt': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'object_sha256': sha(obj), 'base_object': str(BASE.relative_to(ROOT)),
               'base_sha256': sha(BASE), 'linked_object': str(linked.relative_to(ROOT)),
               'linked_sha256': sha(linked), 'source_owned_symbols': sorted(OWNED),
               'unresolved_before': len(before), 'unresolved_after': len(after),
               'imports_resolved': sorted(OWNED), 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False,
               'hardware_proof': False,
               'limits': ['Valid non-null SC CCB contexts were compared; final RAM placement and hardware behavior remain open.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))

if __name__ == '__main__': main()
