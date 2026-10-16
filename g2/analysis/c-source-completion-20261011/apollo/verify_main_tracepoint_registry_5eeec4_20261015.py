#!/usr/bin/env python3
"""Compare tracepoint registry dispatch, logging and role helper to Main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_registry_5eeec4.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-registry-5eeec4'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_uart_device_role_get(void){return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
uint32_t audio_tracepoint_handle_ble_data_5ee8bc(const void*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_tracepoint_handle_slave_file_list_5eeb98(const void*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
''')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_registry_callback_5eeec4',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
    with elf.open('rb') as f:
        segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    def run(compiled, event, present, length, role, log_mask):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for addr, data in segments: u.mem_write(addr, data)
        u.mem_map(0x20000000, 0x100000)
        payload = 0x20073000 if present else 0
        hooks = ({syms['audio_uart_device_role_get'] & ~1: 'role',
                  syms['audio_log_flags'] & ~1: 'flags',
                  syms['audio_log_extended'] & ~1: 'extended',
                  syms['compressed_log_output'] & ~1: 'compact',
                  syms['audio_tracepoint_handle_ble_data_5ee8bc'] & ~1: 'ble',
                  syms['audio_tracepoint_handle_slave_file_list_5eeb98'] & ~1: 'slave',
                  syms['audio_ring_pb_tx_ble_475b14'] & ~1: 'forward'} if compiled else
                 {0x45a568: 'role', 0x43d0ce: 'flags', 0x43d574: 'extended',
                  0x43ce9e: 'compact', 0x5ee8bc: 'ble', 0x5eeb98: 'slave',
                  0x475b14: 'forward'})
        calls = []
        def string(cpu, addr):
            return bytes(cpu.mem_read(addr, 256)).split(b'\0')[0].decode('ascii')
        def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), 'little')
        def hook(cpu, pc, size, user):
            kind = hooks.get(pc)
            if kind is None: return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if kind == 'role': cpu.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0, log_mask)
            elif kind == 'extended':
                calls.append(('extended', r0, string(cpu, r1), string(cpu, r2),
                              string(cpu, r3), word(cpu, sp), string(cpu, word(cpu, sp+4)),
                              word(cpu, sp+8), word(cpu, sp+12), word(cpu, sp+16)))
            elif kind == 'compact':
                calls.append(('compact', r0, string(cpu, r1), string(cpu, r2),
                              r3, word(cpu, sp)) +
                             ((word(cpu, sp+4),) if r0 == 0x10c00000 else ()))
            elif kind == 'ble':
                calls.append(('ble', r0, r1)); cpu.reg_write(A.UC_ARM_REG_R0, 7)
            elif kind == 'slave':
                calls.append(('slave', r0, r1)); cpu.reg_write(A.UC_ARM_REG_R0, 13)
            else:
                calls.append(('forward', r0, r1, r2, r3))
                cpu.reg_write(A.UC_ARM_REG_R0, 23)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        for reg, val in ((A.UC_ARM_REG_R0, event), (A.UC_ARM_REG_R1, payload),
                         (A.UC_ARM_REG_R2, length), (A.UC_ARM_REG_R3, 0x98765432),
                         (A.UC_ARM_REG_SP, 0x2007f000), (A.UC_ARM_REG_LR, 0x600001)):
            u.reg_write(reg, val)
        address = syms['audio_uart_registry_callback_5eeec4'] if compiled else 0x5eeec4
        u.emu_start(address | 1, 0x600000, count=20000)
        return {'return': u.reg_read(A.UC_ARM_REG_R0), 'calls': calls}
    cases = []
    for event in (0, 0xb, 0xc, 0xd):
        for present in (False, True):
            for length in (0, 0x10003):
                for role in (1, 2):
                    for log_mask in (0, 1, 2, 4, 7):
                        native = run(False, event, present, length, role, log_mask)
                        source = run(True, event, present, length, role, log_mask)
                        if native != source:
                            raise AssertionError((event, present, length, role,
                                                  log_mask, native, source))
                        cases.append({'event': event, 'present': present,
                                      'length': length, 'role': role,
                                      'log_mask': log_mask, 'calls': len(native)})
    receipt = {'status': 'PASS_BOUNDED_MAIN_TRACEPOINT_REGISTRY_NATIVE_C',
               'cases': cases, 'source': str(SOURCE.relative_to(ROOT)),
               'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'payload_sha256': PINNED,
               'limits': ['Child handler effects are compared at call boundaries; final placement and hardware are unproved.']}
    path = OUT / 'oracle.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases), hashlib.sha256(path.read_bytes()).hexdigest())
