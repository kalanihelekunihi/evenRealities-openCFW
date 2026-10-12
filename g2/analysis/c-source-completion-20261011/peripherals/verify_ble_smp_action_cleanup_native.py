#!/usr/bin/env python3
"""Compare a pinned Cordio SMP action body with stock ARM effects."""
from pathlib import Path
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

R = Path(__file__).resolve().parents[3]
V = R.parent / 'third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio'
S = R / 'analysis/c-source-completion-20261011/peripherals/smp_tables/candidate_smp_act.c'
B = (R / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
INCLUDES = [R / 'components/bootloader/filesystem/freestanding_include'] + [V / p for p in (
    'ble-host/include', 'ble-host/sources/stack/smp', 'ble-host/sources/stack/cfg',
    'ble-host/sources/stack/dm', 'wsf/include', 'wsf/sources',
    'wsf/sources/port/freertos')]
STUB = '''#include <stdint.h>
uint32_t free_count, stop_count, free_arg, stop_arg0, stop_arg1;
void WsfBufFree(void *p){free_arg=(uint32_t)p;free_count++;}
void WsfTimerStop(void *p){if(stop_count==0)stop_arg0=(uint32_t)p;else stop_arg1=(uint32_t)p;stop_count++;}
'''

with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)
    (t / 'stub.c').write_text(STUB)
    cc = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
          '-O2', '-ffunction-sections', '-fdata-sections']
    subprocess.run(cc + ['-Wno-unused-parameter', *['-I' + str(p) for p in INCLUDES],
                         '-c', str(S), '-o', str(t / 'action.o')], check=True)
    subprocess.run(cc + ['-c', str(t / 'stub.c'), '-o', str(t / 'stub.o')], check=True)
    elf = t / 'action.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-nostdlib', '-Wl,--gc-sections', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,smpCleanup', str(t / 'action.o'), str(t / 'stub.o'),
                    '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segments = [(v['p_vaddr'], v.data()) for v in e.iter_segments()
                    if v['p_type'] == 'PT_LOAD']
        symbols = {v.name: v['st_value'] for v in
                   e.get_section_by_name('.symtab').iter_symbols()}
    for initiator in (0, 1):
        for scratch in (0, 0x20081000):
            pair = []
            for compiled in (False, True):
                u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                u.mem_map(0x400000, 0x400000)
                u.mem_write(0x438000, B)
                u.mem_map(0x100000, 0x100000)
                u.mem_map(0x20000000, 0x100000)
                for a, data in segments:
                    u.mem_write(a, data)
                ccb = 0x20080000
                state = bytearray([0xa5] * 0x50)
                state[0x30:0x34] = scratch.to_bytes(4, 'little')
                state[0x3a] = initiator
                u.mem_write(ccb, bytes(state))
                calls = []
                if not compiled:
                    def hook(uc, pc, size, user):
                        calls.append(('free' if pc == 0x5304d4 else 'stop',
                                      uc.reg_read(UC_ARM_REG_R0)))
                        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                    for a in (0x5304d4, 0x52a4d2):
                        u.hook_add(UC_HOOK_CODE, hook, begin=a, end=a)
                u.reg_write(UC_ARM_REG_R0, ccb)
                u.reg_write(UC_ARM_REG_SP, 0x200ff000)
                u.reg_write(UC_ARM_REG_LR, 0x600001)
                u.emu_start((symbols['smpCleanup'] if compiled else 0x56e5e0) | 1,
                            0x600000, count=3000)
                if compiled:
                    free_count = int.from_bytes(u.mem_read(symbols['free_count'], 4), 'little')
                    stop_count = int.from_bytes(u.mem_read(symbols['stop_count'], 4), 'little')
                    if free_count:
                        calls.append(('free', int.from_bytes(u.mem_read(symbols['free_arg'], 4), 'little')))
                    for i in range(stop_count):
                        key = 'stop_arg0' if i == 0 else 'stop_arg1'
                        calls.append(('stop', int.from_bytes(u.mem_read(symbols[key], 4), 'little')))
                pair.append((bytes(u.mem_read(ccb, 0x50)), calls))
            assert pair[0] == pair[1], (initiator, scratch, pair)
print('PASS_BLE_SMP_ACTION_CLEANUP_NATIVE 4')
