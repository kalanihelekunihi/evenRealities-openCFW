#!/usr/bin/env python3
"""Compare compiled out-of-range Cordio action lookup with pinned ROM bytes."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_update_invalid_event_78eff4.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-update-invalid-event-78eff4'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    action = blob[0x78eff0 - 0x438000:0x78eff8 - 0x438000]
    if action != bytes.fromhex('10 20 11 21 f9 2d 4b 00'):
        raise RuntimeError('Cordio action table adjacency changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / 'candidate.elf'
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_update_invalid_event_action',
                        str(SOURCE), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        entry = symbols['audio_ble_dm_conn_update_invalid_event_action']
        cases = 0
        for event in range(256):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x100000, 0x100000)
            cpu.mem_map(0x20000000, 0x10000)
            for addr, data in segments:
                cpu.mem_write(addr, data)
            cpu.mem_write(0x20001000, bytes((0, 0, event, 0)))
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x300001)
            cpu.emu_start(entry | 1, 0x300000, count=100)
            expected = action[event & 7]
            actual = cpu.reg_read(A.UC_ARM_REG_R0) & 0xff
            if actual != expected:
                raise RuntimeError(f'event {event}: compiled {actual:#x}, stock {expected:#x}')
            cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_INVALID_EVENT_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'stock_table_address': '0x78eff0',
               'stock_table_bytes': action.hex(), 'cases': cases,
               'limits': ['Indices 4..7 are stock out-of-bounds table reads into a neighboring function pointer; the pointer bytes are pinned to this stock layout.',
                          'Final relocation and actual connection-update runtime behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
