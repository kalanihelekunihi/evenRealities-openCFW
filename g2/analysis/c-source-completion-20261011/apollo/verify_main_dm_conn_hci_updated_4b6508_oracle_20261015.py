#!/usr/bin/env python3
"""Compare compiled dmConnSmActHciUpdated with Apollo native body."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_hci_updated_4b6508.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-hci-updated-4b6508'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_dm_connection_records[0x100];
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    if blob[0x4b6508 - 0x438000:0x4b651a - 0x438000] != bytes.fromhex(
            '80 b5 08 00 29 21 81 70 03 49 d1 f8 9c 10 88 47 01 bd'):
        raise RuntimeError('HCI update leaf instructions changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_sm_act_hci_updated_4b6508',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, ccb_seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            callback = 0x2000a001
            record = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            cpu.mem_write(record + 0x9c, callback.to_bytes(4, 'little'))
            ccb = bytes((ccb_seed,) * 32)
            message = bytes((event,) * 32)
            cpu.mem_write(0x20081000, ccb)
            cpu.mem_write(0x20082000, message)
            calls = []
            def hook(uc, addr, size, user):
                if addr == callback - 1:
                    calls.append((uc.reg_read(A.UC_ARM_REG_R0),
                                  bytes(uc.mem_read(0x20082000, 32))))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20081000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20082000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_sm_act_hci_updated_4b6508'] if compiled else 0x4b6508
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20081000, 32)), bytes(cpu.mem_read(0x20082000, 32))

        cases = 0
        for event in range(256):
            for ccb_seed in (0, 0xa5):
                stock = run(False, event, ccb_seed)
                candidate = run(True, event, ccb_seed)
                if stock != candidate:
                    raise RuntimeError(f'event={event} seed={ccb_seed}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_HCI_UPDATED_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native event mutation and callback call across all event bytes and two CCB patterns.',
               'limits': ['Callback behavior and final RAM placement remain open; this verifies the leaf dispatch boundary.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
