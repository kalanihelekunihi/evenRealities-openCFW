#!/usr/bin/env python3
"""Compare pinned Cordio privacy AES dispatch, actions and effects to C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_priv_aes_interface_78a874.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_priv.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-priv-aes-interface-78a874'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_empty_reset_4d29be', 0x4d29bf),
         ('audio_ble_dm_empty_handler_4d29c0', 0x4d29c1),
         ('audio_ble_dm_priv_aes_msg_handler_4d27ce', 0x4d27cf)]
ACTIONS = [('audio_ble_dm_priv_aes_resolve_4d25ba', 0x4d25bb),
           ('audio_ble_dm_priv_aes_generate_4d26ac', 0x4d26ad)]
SHIM = '''#include <stddef.h>
#include <stdint.h>
uint8_t audio_ble_dm_handler_state[24];
__attribute__((noinline)) void audio_ble_dm_empty_reset_4d29be(void){}
__attribute__((noinline)) void audio_ble_dm_empty_handler_4d29c0(void*x){(void)x;}
__attribute__((noinline)) int memcmp(const void*x,const void*y,size_t n){(void)x;(void)y;(void)n;return 0;}
__attribute__((noinline)) void *memcpy(void*x,const void*y,size_t n){(void)y;(void)n;return x;}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmPrivAesMsgHandler(wsfMsgHdr_t *pMsg)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    stock_table = struct.unpack_from('<III', blob, 0x78a874-0x438000)
    stock_actions = struct.unpack_from('<II', blob, 0x78d454-0x438000)
    if stock_table != tuple(x for _, x in SLOTS) or \
            stock_actions != tuple(x for _, x in ACTIONS):
        raise RuntimeError('native privacy AES interface changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_priv_aes_msg_handler_4d27ce',
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
        table = struct.unpack('<III', read_elf(symbols['audio_ble_dm_priv_table_b'], 12))
        actions = struct.unpack('<II', read_elf(symbols['audio_ble_dm_priv_aes_actions'], 8))
        if table != tuple(symbols[name] for name, _ in SLOTS) or \
                actions != tuple(symbols[name] for name, _ in ACTIONS):
            raise RuntimeError('C privacy AES pointer slots changed')

        def run(compiled, index, equal, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            state = symbols['audio_ble_dm_priv_cb_storage'] if compiled else 0x20073a58
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            cpu.mem_write(dm + 8, (0x20007001).to_bytes(4, 'little'))
            cb = bytearray((seed + i * 5) & 0xff for i in range(26))
            cb[0:3] = b'\x11\x22\x33'
            cb[3] = 0xff
            cpu.mem_write(state, bytes(cb))
            ciphertext = bytearray((seed + i * 7) & 0xff for i in range(16))
            ciphertext[:3] = b'\x11\x22\x33' if equal else b'\x11\x22\x34'
            cpu.mem_write(0x20005000, bytes(ciphertext))
            msg = bytearray((seed + i * 3) & 0xff for i in range(24))
            msg[2] = 0x40 + index
            msg[4:8] = (0x20005000).to_bytes(4, 'little')
            cpu.mem_write(0x20001000, bytes(msg))
            cmp_addr = (symbols['memcmp'] if compiled else 0x4751c8) & ~1
            copy_addr = (symbols['memcpy'] if compiled else 0x439be4) & ~1
            calls = []
            def hook(uc, addr, size, user):
                if addr == cmp_addr:
                    left = uc.reg_read(A.UC_ARM_REG_R0)
                    right = uc.reg_read(A.UC_ARM_REG_R1)
                    n = uc.reg_read(A.UC_ARM_REG_R2)
                    calls.append(('cmp', n, bytes(uc.mem_read(left, n)).hex(),
                                  bytes(uc.mem_read(right, n)).hex()))
                    x, y = bytes(uc.mem_read(left, n)), bytes(uc.mem_read(right, n))
                    result = next((a-b for a, b in zip(x, y) if a != b), 0)
                    uc.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == copy_addr:
                    dst = uc.reg_read(A.UC_ARM_REG_R0)
                    src = uc.reg_read(A.UC_ARM_REG_R1)
                    n = uc.reg_read(A.UC_ARM_REG_R2)
                    calls.append(('copy', n, bytes(uc.mem_read(src, n)).hex()))
                    uc.mem_write(dst, bytes(uc.mem_read(src, n)))
                    uc.reg_write(A.UC_ARM_REG_R0, dst)
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                elif addr == 0x20007000:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    calls.append(('callback', bytes(uc.mem_read(ptr, 24)).hex()))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_priv_aes_msg_handler_4d27ce'] if compiled else 0x4d27ce
            cpu.emu_start(entry | 1, 0x600000, count=700)
            return calls, bytes(cpu.mem_read(0x20001000, 24)), bytes(cpu.mem_read(state, 26))

        cases = 0
        for index in (0, 1):
            for equal in (False, True):
                for seed in (0, 0x45, 0xa5):
                    stock = run(False, index, equal, seed)
                    candidate = run(True, index, equal, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{index=} {equal=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_PRIV_AES_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA,
               'native_slots': [hex(x) for x in stock_table],
               'native_actions': [hex(x) for x in stock_actions], 'cases': cases,
               'comparison_scope': 'Three interface and two action slots, AES resolve/generate callback bytes, three-byte compare/copy and 26-byte privacy state effects.',
               'limits': ['Only valid privacy AES action indices zero and one are compared; final RAM placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
