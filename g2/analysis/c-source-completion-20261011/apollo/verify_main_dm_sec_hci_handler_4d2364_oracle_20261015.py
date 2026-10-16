#!/usr/bin/env python3
"""Compare native Cordio security HCI dispatch and the C candidate."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_sec_hci_handler_4d2364.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_sec.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-sec-hci-handler-4d2364'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];
__attribute__((noinline)) uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t x){(void)x;return 0;}
__attribute__((noinline)) int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
__attribute__((noinline)) uint8_t *audio_ble_smp_get_stk_537c4c(uint8_t x,uint8_t*y){(void)x;(void)y;return 0;}
__attribute__((noinline)) uint8_t audio_ble_smp_lesc_enabled_537c30(uint8_t x){(void)x;return 0;}
__attribute__((noinline)) void HciLeLtkReqReplCmd(uint16_t x,const uint8_t*y){(void)x;(void)y;}
__attribute__((noinline)) void HciLeLtkReqNegReplCmd(uint16_t x){(void)x;}
__attribute__((noinline)) void DmConnSetIdle(uint8_t x,uint16_t y,uint8_t z){(void)x;(void)y;(void)z;}
__attribute__((noinline)) void DmSmpCbackExec(void*x){(void)x;}
__attribute__((noinline)) void audio_ble_smp_encrypt_ind_537be6(void*x){(void)x;}
'''
TARGETS = {
    'lookup': ('audio_ble_dm_conn_ccb_by_handle_4b601c', 0x4b601c),
    'memcmp': ('g2_lfs_memcmp', 0x4751c8),
    'stk': ('audio_ble_smp_get_stk_537c4c', 0x537c4c),
    'lesc': ('audio_ble_smp_lesc_enabled_537c30', 0x537c30),
    'repl': ('HciLeLtkReqReplCmd', 0x52b2ce),
    'neg': ('HciLeLtkReqNegReplCmd', 0x52b2a4),
    'idle': ('DmConnSetIdle', 0x4b71dc),
    'smp_cb': ('DmSmpCbackExec', 0x4d24a8),
    'encrypt': ('audio_ble_smp_encrypt_ind_537be6', 0x537be6),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA or \
            'void dmSecHciHandler(hciEvt_t *pEvent)' not in UPSTREAM.read_text():
        raise RuntimeError('native payload or Cordio source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_dispatch_4d2364',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, code, has_ccb, ediv, rand_equal, key_available,
                lesc, status):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            dm = symbols['audio_ble_dm_handler_state'] if compiled else 0x20073b78
            cpu.mem_write(dm, bytes(24))
            cpu.mem_write(dm + 8, (0x110001).to_bytes(4, 'little'))
            ccb = bytearray((i * 3 + 0x23) & 0xff for i in range(64))
            ccb[0x10], ccb[0x12], ccb[0x17], ccb[0x18] = 3, 1, 2, 4
            cpu.mem_write(0x20003000, bytes(ccb))
            cpu.mem_write(0x20004000, bytes((i + 1) & 0xff for i in range(16)))
            event = bytearray((i * 7 + 0x31) & 0xff for i in range(24))
            event[0:2] = (0x1234).to_bytes(2, 'little')
            event[2], event[3] = code, status
            event[0x0e:0x10] = ediv.to_bytes(2, 'little')
            cpu.mem_write(0x20001000, bytes(event))
            addr_to_name = {((symbols[sym] if compiled else stock) & ~1): name
                            for name, (sym, stock) in TARGETS.items()}
            calls = []
            def record_event(uc, ptr):
                raw = bytes(uc.mem_read(ptr, 5))
                return (int.from_bytes(raw[:2], 'little'), raw[2], raw[3],
                        raw[4] if raw[2] == 0x2c else None)
            def hook(uc, addr, size, user):
                if addr == 0x110000:
                    calls.append(('callback', record_event(uc, uc.reg_read(A.UC_ARM_REG_R0))))
                elif addr in addr_to_name:
                    name = addr_to_name[addr]
                    r0 = uc.reg_read(A.UC_ARM_REG_R0)
                    r1 = uc.reg_read(A.UC_ARM_REG_R1)
                    r2 = uc.reg_read(A.UC_ARM_REG_R2)
                    if name == 'lookup':
                        calls.append((name, r0 & 0xffff))
                        uc.reg_write(A.UC_ARM_REG_R0, 0x20003000 if has_ccb else 0)
                    elif name == 'memcmp':
                        calls.append((name, r2))
                        uc.reg_write(A.UC_ARM_REG_R0, 0 if rand_equal else 1)
                    elif name == 'stk':
                        calls.append((name, r0 & 0xff))
                        uc.mem_write(r1, bytes((7,)))
                        uc.reg_write(A.UC_ARM_REG_R0, 0x20004000 if key_available else 0)
                    elif name == 'lesc':
                        calls.append((name, r0 & 0xff))
                        uc.reg_write(A.UC_ARM_REG_R0, lesc)
                    elif name == 'repl':
                        calls.append((name, r0 & 0xffff, r1 == 0x20004000))
                    elif name == 'neg':
                        calls.append((name, r0 & 0xffff))
                    elif name == 'idle':
                        calls.append((name, r0 & 0xff, r1 & 0xffff, r2 & 0xff))
                    elif name in ('smp_cb', 'encrypt'):
                        calls.append((name, record_event(uc, r0)))
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_dispatch_4d2364'] if compiled else 0x4d2364
            try:
                cpu.emu_start(entry | 1, 0x600000, count=2000)
            except Exception as exc:
                raise RuntimeError(f'{compiled=} {code=} {has_ccb=} pc={cpu.reg_read(A.UC_ARM_REG_PC):#x} calls={calls}') from exc
            return calls, bytes(cpu.mem_read(0x20003000, 64)), bytes(cpu.mem_read(0x20001000, 24))

        cases = 0
        for code in (0x10, 0x0e, 0x0f, 0x20):
            for has_ccb in (False, True):
                for ediv in (0, 1):
                    for rand_equal in (False, True):
                        for key_available in (False, True):
                            for lesc in (0, 1):
                                for status in (0, 1):
                                    stock = run(False, code, has_ccb, ediv, rand_equal,
                                                key_available, lesc, status)
                                    candidate = run(True, code, has_ccb, ediv, rand_equal,
                                                    key_available, lesc, status)
                                    if stock != candidate:
                                        raise RuntimeError(f'{code=} {has_ccb=} {ediv=} {rand_equal=} {key_available=} {lesc=} {status=}: {stock} != {candidate}')
                                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_SEC_HCI_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)), 'upstream_sha256': sha(UPSTREAM),
               'payload_sha256': PINNED_SHA, 'cases': cases,
               'comparison_scope': 'Native LTK/STK, LESC, encrypt change/refresh call order, CCB and event fields.',
               'limits': ['Child cryptographic/HCI effects and uninitialized native failure-event padding are outside this comparison.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases, sha(path))

if __name__ == '__main__': main()
