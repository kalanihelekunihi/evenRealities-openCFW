#!/usr/bin/env python3
"""Compare pinned Cordio LESC dispatch and message effects against C."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_lesc_interface_78a8a4.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_sec_lesc.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-lesc-interface-78a8a4'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_empty_reset_4d29be', 0x4d29bf),
         ('audio_ble_dm_empty_handler_4d29c0', 0x4d29c1),
         ('audio_ble_dm_lesc_msg_handler_534894', 0x534895)]
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[24];
__attribute__((noinline)) void audio_ble_dm_empty_reset_4d29be(void){}
__attribute__((noinline)) void audio_ble_dm_empty_handler_4d29c0(void*x){(void)x;}
__attribute__((noinline)) void WsfBufFree(void*x){(void)x;}
__attribute__((noinline)) void Calc128Cpy(void*x,const void*y){(void)x;(void)y;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmSecLescMsgHandler(dmSecMsg_t *pMsg)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    stock_table = struct.unpack_from('<III', blob, 0x78a8a4 - 0x438000)
    if stock_table != tuple(address for _, address in SLOTS):
        raise RuntimeError('native LESC interface changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_lesc_msg_handler_534894',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}
        def read_elf(address, size):
            for base, data in segments:
                if base <= address and address + size <= base + len(data):
                    return data[address-base:address-base+size]
            raise RuntimeError('table not in load segments')
        table = struct.unpack('<III', read_elf(symbols['audio_ble_dm_lesc_table'], 12))
        if table != tuple(symbols[name] for name, _ in SLOTS):
            raise RuntimeError('C LESC interface slots changed')

        def run(compiled, kind, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            rand_cell = symbols['audio_ble_dm_lesc_oob_rand'] if compiled else 0x200744f8
            cpu.mem_write(dm + 8, (0x20007001).to_bytes(4, 'little'))
            cpu.mem_write(rand_cell, (0x20004000).to_bytes(4, 'little'))
            rand = bytes((seed + i * 5) & 0xff for i in range(16))
            cipher = bytes((seed + i * 7) & 0xff for i in range(16))
            cpu.mem_write(0x20004000, rand)
            cpu.mem_write(0x20005000, cipher)
            cpu.mem_write(0x20006000, bytes(range(16)))
            message = bytearray((seed + i * 3) & 0xff for i in range(24))
            message[2] = kind
            message[4:8] = (0x20005000).to_bytes(4, 'little')
            message[8:12] = (0x20006000).to_bytes(4, 'little')
            cpu.mem_write(0x20001000, bytes(message))
            free_addr = (symbols['WsfBufFree'] if compiled else 0x5304d4) & ~1
            copy_addr = (symbols['Calc128Cpy'] if compiled else 0x542a44) & ~1
            calls = []
            def hook(uc, addr, size, user):
                if addr == free_addr:
                    calls.append(('free', uc.reg_read(A.UC_ARM_REG_R0)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == copy_addr:
                    dst = uc.reg_read(A.UC_ARM_REG_R0)
                    src = uc.reg_read(A.UC_ARM_REG_R1)
                    calls.append(('copy', src))
                    uc.mem_write(dst, bytes(uc.mem_read(src, 16)))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    if ptr == 0x20001000:
                        calls.append(('callback_message', bytes(uc.mem_read(ptr, 24)).hex()))
                    else:
                        calls.append(('callback_oob', bytes(uc.mem_read(ptr+2, 34)).hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_lesc_msg_handler_534894'] if compiled else 0x534894
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 24))

        cases = 0
        for kind in (0x40, 0x41, 0x42):
            for seed in (0, 0x45, 0xa5, 0xff):
                stock = run(False, kind, seed)
                candidate = run(True, kind, seed)
                if stock != candidate:
                    raise RuntimeError(f'{kind=} {seed=}: {stock} != {candidate}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_LESC_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'native_slots': [hex(x) for x in stock_table],
               'cases': cases,
               'comparison_scope': 'Three LESC table pointers, ECC event forwarding and OOB free/copy/callback order and payload.',
               'limits': ['OOB event header bytes zero and one are uninitialized and excluded; child callback/free effects, placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
