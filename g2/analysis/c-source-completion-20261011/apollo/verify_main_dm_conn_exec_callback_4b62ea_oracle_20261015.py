#!/usr/bin/env python3
"""Compare Cordio five-callback fanout with Apollo native body."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn_exec_callback_4b62ea.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn-exec-callback-4b62ea'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = 'unsigned char audio_dm_connection_records[0x100];\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn_exec_callback_4b62ea',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, mask, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            record = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            callbacks = bytearray(20)
            addresses = [0x2000a001 + i * 0x20 for i in range(5)]
            for i, target in enumerate(addresses):
                if mask & (1 << i):
                    callbacks[4 * i:4 * i + 4] = target.to_bytes(4, 'little')
            cpu.mem_write(record + 0x90, bytes(callbacks))
            cpu.mem_write(0x20081000, bytes((seed,) * 32))
            calls = []
            def hook(uc, address, size, user):
                if address in (x & ~1 for x in addresses):
                    calls.append((addresses.index(address | 1),
                                  uc.reg_read(A.UC_ARM_REG_R0),
                                  bytes(uc.mem_read(0x20081000, 32))))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20081000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn_exec_callback_4b62ea'] if compiled else 0x4b62ea
            cpu.emu_start(entry | 1, 0x600000, count=3000)
            return calls, bytes(cpu.mem_read(record + 0x90, 20))

        cases = 0
        for mask in range(32):
            for seed in (0, 0x55, 0xff):
                stock = run(False, mask, seed)
                candidate = run(True, mask, seed)
                if stock != candidate:
                    raise RuntimeError(f'{mask=} {seed=}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN_EXEC_CALLBACK_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native callback order and event forwarding for all five-slot occupancy masks.',
               'limits': ['Callback bodies and user effects remain outside this source slice.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
