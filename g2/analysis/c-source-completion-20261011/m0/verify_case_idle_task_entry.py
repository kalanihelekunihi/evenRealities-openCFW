#!/usr/bin/env python3
"""Bounded stock/C idle-task iteration comparison at child-call boundaries."""
from pathlib import Path
import random, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
with (HERE / 'case_absolute_experiment.elf').open('rb') as stream:
    image = ELFFile(stream)
    symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
    segments = [(p['p_vaddr'], p.data()) for p in image.iter_segments() if p['p_type'] == 'PT_LOAD']
rng = random.Random(0xae5c)
for index in range(256):
    ready = rng.choice((0, 1, 2, 3, 0x80000000, 0xffffffff))
    pair = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_write(0x20000ff4, struct.pack('<I', ready))
        u.reg_write(UC_ARM_REG_R0, 0x12345678)
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        targets = ({0x0800ace4: 'maintenance', 0x0800c0a0: 'reschedule'} if native else
                   {symbols['case_boot_idle_maintenance'] & ~1: 'maintenance',
                    symbols['case_policy_task_reschedule'] & ~1: 'reschedule'})
        calls = []
        def hook(uc, address, size, user):
            kind = targets.get(address)
            if kind is None:
                return
            calls.append(kind)
            if calls.count('maintenance') == 2:
                uc.emu_stop()
                return
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x0800ae5c if native else symbols['case_boot_idle_task_entry'] & ~1
        u.emu_start(entry | 1, 0, count=64)
        pair.append((calls, bytes(u.mem_read(0x20000ff4, 4))))
    assert pair[0] == pair[1], (index, ready, pair)
print('PASS_CASE_IDLE_TASK_ENTRY', 256)
