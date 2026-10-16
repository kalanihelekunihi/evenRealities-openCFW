#!/usr/bin/env python3
"""Compare ALS registry paths and logging gates with authenticated Apollo code."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/als_sync_registry_4ae73c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-als-sync-registry-4ae73c'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
assert int.from_bytes(blob[0x46c6a8-0x438000:0x46c6ac-0x438000], 'little') == 0x20072da8
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[0x50];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
uint32_t g2_display_state_table[16];
uint32_t audio_settings_notify_device_status(void){return 0;}
''')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_registry_callback_4ae73c',
                    str(SRC), str(shim), '-o', str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
    with elf.open('rb') as f:
        segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    def run(compiled, length, level, notify, log_mask):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for addr, data in segments: u.mem_write(addr, data)
        u.mem_map(0x20000000, 0x100000)
        arg = 0x20073000; record = 0x20072da8
        u.mem_write(arg, bytes((level, notify, 0x5a)))
        u.mem_write(0x20071014, (0x20072001).to_bytes(4, 'little'))
        u.mem_write(syms['g2_display_state_table'] + 0x14,
                    (0x20072001).to_bytes(4, 'little'))
        calls = []
        if compiled:
            address = syms['audio_uart_registry_callback_4ae73c']
            hooks = {syms['audio_log_flags'] & ~1: 'flags',
                     syms['audio_als_callback_context_47394c'] & ~1: 'context',
                     syms['audio_settings_notify_device_status'] & ~1: 'notify',
                     syms['audio_log_extended'] & ~1: 'extended',
                     syms['compressed_log_output'] & ~1: 'compact',
                     0x20072000: 'callback'}
            data_addr = syms['audio_settings_config_live']
        else:
            address = 0x4ae73c
            hooks = {0x43d0ce: 'flags', 0x47394c: 'context',
                     0x49be04: 'notify', 0x43d574: 'extended',
                     0x43ce9e: 'compact', 0x20072000: 'callback'}
            data_addr = record
        def text_at(cpu, addr):
            if addr == 0: return ''
            return bytes(cpu.mem_read(addr, 256)).split(b'\0')[0].decode('ascii')
        def word_at(cpu, addr):
            return int.from_bytes(cpu.mem_read(addr, 4), 'little')
        def hook(cpu, pc, size, user):
            kind = hooks.get(pc)
            if kind is None: return
            if kind == 'callback':
                calls.append(('callback', cpu.reg_read(A.UC_ARM_REG_R0)))
            elif kind == 'context':
                calls.append(('context',))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x20071000)
            elif kind == 'extended':
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                calls.append(('extended', cpu.reg_read(A.UC_ARM_REG_R0),
                              text_at(cpu, cpu.reg_read(A.UC_ARM_REG_R1)),
                              text_at(cpu, cpu.reg_read(A.UC_ARM_REG_R2)),
                              text_at(cpu, cpu.reg_read(A.UC_ARM_REG_R3)),
                              word_at(cpu, sp), text_at(cpu, word_at(cpu, sp+4)),
                              word_at(cpu, sp+8), word_at(cpu, sp+12)))
            elif kind == 'compact':
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                calls.append(('compact', cpu.reg_read(A.UC_ARM_REG_R0),
                              text_at(cpu, cpu.reg_read(A.UC_ARM_REG_R1)),
                              text_at(cpu, cpu.reg_read(A.UC_ARM_REG_R2)),
                              cpu.reg_read(A.UC_ARM_REG_R3), word_at(cpu, sp)))
            elif kind == 'notify':
                calls.append(('notify',))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            else:
                calls.append(('flags',))
                cpu.reg_write(A.UC_ARM_REG_R0, log_mask)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        for reg, value in ((A.UC_ARM_REG_R0, 0x104), (A.UC_ARM_REG_R1, arg),
                           (A.UC_ARM_REG_R2, length), (A.UC_ARM_REG_SP, 0x2007f000),
                           (A.UC_ARM_REG_LR, 0x600001)):
            u.reg_write(reg, value)
        u.emu_start(address | 1, 0x600000, count=20000)
        return {'return': u.reg_read(A.UC_ARM_REG_R0),
                'calls': [c for c in calls if c[0] not in ('flags', 'context')],
                'settings_byte': bytes(u.mem_read(data_addr + 1, 1)).hex()}
    cases = []
    for length in (0, 1, 2, 3, 255):
        for level, notify in ((0, 0), (37, 0), (100, 1), (255, 255)):
            for log_mask in (0, 1, 2, 4, 7):
                native = run(False, length, level, notify, log_mask)
                source = run(True, length, level, notify, log_mask)
                if native != source:
                    raise AssertionError((length, level, notify, log_mask, native, source))
                cases.append({'length': length, 'level': level, 'notify': notify,
                              'log_mask': log_mask, **native})
    path = OUT / 'oracle.json'
    receipt = {'status': 'PASS_BOUNDED_MAIN_ALS_SYNC_NATIVE_C', 'cases': cases,
               'source': str(SRC.relative_to(ROOT)),
               'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PINNED, 'logging_masks': [0, 1, 2, 4, 7],
               'limits': ['Final Main placement and hardware execution are not compared.']}
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases), hashlib.sha256(path.read_bytes()).hexdigest())
