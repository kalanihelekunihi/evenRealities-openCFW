#!/usr/bin/env python3
"""Compare Apollo registration allocation-failure callback path."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_audio_enqueue_alloc_failure_45f402.c'
CONTEXT = G2 / 'components/audio/uart_thread_source_candidate/display_audio_registration_assert_context_45f678.c'
OUT = G2 / 'build/c-firmware/20261015/main-audio-enqueue-alloc-failure-45f402'
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
void (*g2_extended_log_fatal_callback)(const void*,const char*,uint32_t);
__attribute__((noinline)) uint32_t audio_log_level(void){return 0;}
__attribute__((noinline)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
__attribute__((noinline)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
__attribute__((noinline)) void audio_ble_radio_ready_44b0ae(void){}
'''

def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, 'little'))

def get(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 4), 'little')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError('Apollo payload changed')
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                        '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_uart_display_audio_allocation_fatal_45f402',
                        str(SRC), str(CONTEXT), str(shim), '-o', str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ['arm-none-eabi-nm', str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open('rb') as f:
            segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                        if s['p_type'] == 'PT_LOAD']

        def run(compiled, mask, callback_valid):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            cell = syms['g2_extended_log_fatal_callback'] if compiled else 0x2007456c
            put(cpu, cell, 0x20018001 if callback_valid else 0)
            targets = {
                (syms['audio_log_level'] if compiled else 0x43d0ce) & ~1: 'level',
                (syms['audio_log_extended'] if compiled else 0x43d574) & ~1: 'extended',
                (syms['compressed_log_output'] if compiled else 0x43ce9e) & ~1: 'compact',
                0x20018000: 'fatal_callback',
                (syms['audio_ble_radio_ready_44b0ae'] if compiled else 0x44b0ae) & ~1: 'reset'}
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            trace = []
            def cstring(ptr):
                return bytes(cpu.mem_read(ptr, 160)).split(b'\x00', 1)[0].decode('utf-8')
            def hook(cpu, address, size, _):
                key = targets.get(address)
                if key is None:
                    return
                vals = tuple(cpu.reg_read(r) for r in regs)
                if key == 'extended':
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    item = (key, vals[0], *(cstring(v) for v in vals[1:]),
                            get(cpu, sp), cstring(get(cpu, sp + 4)))
                    if vals[0] == 0:
                        item += (bytes(cpu.mem_read(get(cpu, sp + 8), 4)),
                                 cstring(get(cpu, sp + 12)), get(cpu, sp + 16))
                    trace.append(item)
                elif key == 'compact':
                    trace.append((key, vals[0], cstring(vals[1]), cstring(vals[2])))
                elif key == 'fatal_callback':
                    trace.append((key, bytes(cpu.mem_read(vals[0], 4)),
                                  cstring(vals[1]), vals[2]))
                elif key == 'reset':
                    trace.append((key,))
                    cpu.emu_stop()
                    return
                cpu.reg_write(A.UC_ARM_REG_R0, mask if key == 'level' else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            sp = 0x203ff000
            if not compiled:
                sp -= 40
                put(cpu, sp + 36, 0x600001)
            cpu.reg_write(A.UC_ARM_REG_SP, sp)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = (syms['audio_uart_display_audio_allocation_fatal_45f402']
                     if compiled else 0x45f402)
            cpu.emu_start(start | 1, 0x600000, count=300)
            return trace

        cases = 0
        for callback_valid in (False, True):
            for mask in (0, 1, 2, 4, 7):
                stock, rebuilt = run(False, mask, callback_valid), run(True, mask, callback_valid)
                if stock != rebuilt:
                    raise RuntimeError(f'allocation-failure mismatch {mask},{callback_valid}: {stock} != {rebuilt}')
                cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_AUDIO_ALLOC_FAILURE_ORACLE',
               'cases': cases, 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'context_source_sha256': hashlib.sha256(CONTEXT.read_bytes()).hexdigest(),
               'payload_sha256': PAYLOAD_SHA,
               'limits': ['Callback-present and null-callback failure logs compared.',
                          'Null-callback reset observed through its first call; live reset remains open.']}
    (OUT / 'oracle.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
