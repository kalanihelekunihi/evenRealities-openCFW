#!/usr/bin/env python3
"""Compare the complete timer reload body at its child/callback boundaries."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE = ROOT / 'g2/components/audio/source_candidate_20261010/timer_reload_provider.c'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK = Path('/tmp/audio-timer-reload.ld')
ELF = Path('/tmp/audio-timer-reload.elf')
LINK.write_text('audio_timer_reload_insert = 0x47e93d; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC), '-mcpu=cortex-m4', '-mthumb', '-Og', '-ffreestanding',
                '-fno-builtin', '-nostdlib', '-T', str(LINK), str(SOURCE), '-o', str(ELF)], check=True)
raw = OTA.read_bytes()[32:]
with ELF.open('rb') as f:
    elf = ELFFile(f)
    code = elf.get_section_by_name('.text').data()
    symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == 'stock_timer_reload')
    source_entry = symbol['st_value'] | 1

def run(original, period, expiry, now, returns, callback_delta):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x2000)
    u.mem_write(0x100000, code)
    u.mem_map(0x20000000, 0x80000)
    timer = 0x20010000
    state = bytearray(40)
    struct.pack_into('<I', state, 24, period)
    struct.pack_into('<I', state, 32, 0x100601)
    u.mem_write(timer, bytes(state))
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100801)
    for register, value in ((UC_ARM_REG_R0, timer), (UC_ARM_REG_R1, expiry), (UC_ARM_REG_R2, now)):
        u.reg_write(register, value)
    events = []
    index = [0]
    done = [False]

    def hook(cpu, address, _size, _):
        if address == 0x100800:
            done[0] = True
            cpu.emu_stop()
        elif address == 0x47e93c:
            args = [cpu.reg_read(x) for x in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]
            events.append(['insert', *args])
            if index[0] >= len(returns):
                raise AssertionError('extra insert call')
            cpu.reg_write(UC_ARM_REG_R0, returns[index[0]])
            index[0] += 1
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address == 0x100600:
            events.append(['callback', cpu.reg_read(UC_ARM_REG_R0)])
            current = struct.unpack('<I', cpu.mem_read(timer + 24, 4))[0]
            cpu.mem_write(timer + 24, struct.pack('<I', (current + callback_delta) & 0xffffffff))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start(0x47e813 if original else source_entry, 0x100900, count=500)
    assert done[0] and index[0] == len(returns), (events, done, index)
    return {'events': events, 'timer': u.mem_read(timer, 40).hex(),
            'sp': u.reg_read(UC_ARM_REG_SP), 'pc': u.reg_read(UC_ARM_REG_PC)}

cases = []
for period in (0, 1, 17, 0xfffffffe):
    for expiry in (0, 3, 0xfffffff0):
        for now in (0, 9, 0xffffffff):
            for returns in ((0,), (1, 0), (1, 1, 0)):
                for delta in (0, 2):
                    old = run(True, period, expiry, now, returns, delta)
                    new = run(False, period, expiry, now, returns, delta)
                    assert old == new, (period, expiry, now, returns, delta, old, new)
                    cases.append({'period': period, 'expiry': expiry, 'now': now,
                                  'child_returns': returns, 'callback_period_delta': delta, 'state': old})

result = {'status': 'PASS', 'fresh_cases': len(cases), 'original_entry': '0x47e812',
          'ota_sha256': hashlib.sha256(OTA.read_bytes()).hexdigest(),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'gcc_sha256': hashlib.sha256(GCC.read_bytes()).hexdigest(),
          'link_script': LINK.read_text(), 'cases': cases,
          'limits': ['Child 0x47E93C and timer callback are intercepted at their exact call ABI. Their bodies, daemon scheduling, and callback effects beyond the modeled period update are separate.']}
Path(__file__).with_name('timer-reload-execution.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS', len(cases), 'timer reload original/source cases')
