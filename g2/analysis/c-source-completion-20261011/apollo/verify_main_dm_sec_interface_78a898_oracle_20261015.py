#!/usr/bin/env python3
"""Compare the native Cordio security interface and message handler to C."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_sec_interface_78a898.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_sec.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-sec-interface-78a898'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SLOTS = [('audio_ble_dm_dispatch_4d2544', 0x4d2545),
         ('audio_ble_dm_dispatch_4d2364', 0x4d2365),
         ('audio_ble_dm_sec_msg_handler_4d2440', 0x4d2441)]
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void audio_ble_dm_dispatch_4d2544(void*x){(void)x;}
__attribute__((noinline)) void audio_ble_dm_dispatch_4d2364(void*x){(void)x;}
__attribute__((noinline)) uint8_t *dmConnCcbById(uint8_t x){(void)x;return 0;}
__attribute__((noinline)) void DmConnSetIdle(uint8_t a,uint16_t b,uint8_t c){(void)a;(void)b;(void)c;}
__attribute__((noinline)) void HciLeStartEncryptionCmd(uint16_t a,const uint8_t*b,uint16_t c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
__attribute__((noinline)) void HciLeLtkReqReplCmd(uint16_t a,const uint8_t*b){(void)a;(void)b;}
__attribute__((noinline)) void HciLeLtkReqNegReplCmd(uint16_t a){(void)a;}
'''
TARGETS = {
    'lookup': ('dmConnCcbById', 0x4b62a8),
    'idle': ('DmConnSetIdle', 0x4b71dc),
    'start': ('HciLeStartEncryptionCmd', 0x52b5a2),
    'repl': ('HciLeLtkReqReplCmd', 0x52b2ce),
    'neg': ('HciLeLtkReqNegReplCmd', 0x52b2a4),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmSecMsgHandler(dmSecMsg_t *pMsg)' not in UPSTREAM.read_text():
        raise RuntimeError('Apollo payload or Cordio source changed')
    stock_table = struct.unpack_from('<III', blob, 0x78a898-0x438000)
    if stock_table != tuple(address for _, address in SLOTS):
        raise RuntimeError('native security interface changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_sec_msg_handler_4d2440',
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
        table = struct.unpack('<III', read_elf(symbols['audio_ble_dm_security_table'], 12))
        if table != tuple(symbols[name] for name, _ in SLOTS):
            raise RuntimeError('C security interface slots changed')

        def run(compiled, code, present, found, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            ccb = bytearray((seed + i * 5) & 0xff for i in range(64))
            ccb[0x0c:0x0e] = (0x1234).to_bytes(2, 'little')
            ccb[0x10] = 3
            cpu.mem_write(0x20003000, bytes(ccb))
            message = bytearray((seed + i * 7) & 0xff for i in range(40))
            message[0:2] = (3).to_bytes(2, 'little')
            message[2] = code
            message[0x14] = found
            message[0x15] = 7
            message[0x1c:0x1e] = (0xabcd).to_bytes(2, 'little')
            message[0x1e] = 5
            cpu.mem_write(0x20001000, bytes(message))
            lookup = {((symbols[sym] if compiled else stock) & ~1): name
                      for name, (sym, stock) in TARGETS.items()}
            calls = []
            def hook(uc, addr, size, user):
                if addr not in lookup:
                    return
                name = lookup[addr]
                r = [uc.reg_read(getattr(A, f'UC_ARM_REG_R{i}')) for i in range(4)]
                if name == 'lookup':
                    calls.append((name, r[0] & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20003000 if present else 0)
                elif name == 'idle':
                    calls.append((name, r[0] & 0xff, r[1] & 0xffff, r[2] & 0xff))
                elif name == 'start':
                    calls.append((name, r[0] & 0xffff, r[1]-0x20001000,
                                  r[2] & 0xffff, r[3]-0x20001000))
                elif name == 'repl':
                    calls.append((name, r[0] & 0xffff, r[1]-0x20001000))
                elif name == 'neg':
                    calls.append((name, r[0] & 0xffff))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_sec_msg_handler_4d2440'] if compiled else 0x4d2440
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20003000, 64)), bytes(cpu.mem_read(0x20001000, 40))

        cases = 0
        for code in (0x28, 0x29, 0x2a):
            for present in (False, True):
                for found in (0, 1):
                    for seed in (0, 0x45, 0xa5):
                        stock = run(False, code, present, found, seed)
                        candidate = run(True, code, present, found, seed)
                        if stock != candidate:
                            raise RuntimeError(f'{code=} {present=} {found=} {seed=}: {stock} != {candidate}')
                        cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_SEC_INTERFACE_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'native_slots': [hex(x) for x in stock_table],
               'cases': cases,
               'comparison_scope': 'Three security table pointers and native encrypt request/LTK response routing, CCB effects and arguments.',
               'limits': ['Child HCI effects, final ROM placement and hardware behavior remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
