#!/usr/bin/env python3
"""Bounded stock/C indirect callback dispatch at CASE 0x8558."""
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
rng = random.Random(0x8558)
for index in range(256):
    task = 0x20001000 + 4 * rng.randrange(200)
    argument = rng.getrandbits(32)
    context = 0 if index % 4 == 0 else 0x20002000
    pair = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_write(0x20002000, struct.pack('<2I', 0x20003001, argument))
        u.reg_write(UC_ARM_REG_R0, task)
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        lower = 0x0800b4a4 if native else symbols['case_boot_transport_task_context'] & ~1
        calls = []
        def hook(uc, address, size, user):
            if address == lower:
                calls.append(('lookup', uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0, context)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == 0x20003000:
                calls.append(('callback', uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x08008558 if native else symbols['case_boot_transport_entry_8558'] & ~1
        u.emu_start(entry | 1, 0x20009000, count=80)
        pair.append(calls)
    assert pair[0] == pair[1] == ([('lookup', task)] +
                                  ([('callback', argument)] if context else [])), (index, pair)
print('PASS_CASE_TRANSPORT_TRAMPOLINE', 256)
