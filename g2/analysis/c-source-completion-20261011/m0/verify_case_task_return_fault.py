#!/usr/bin/env python3
"""Native/source fatal task-return branch and CPSID loop equivalence."""
from pathlib import Path
import struct
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
entry_c = symbols['case_boot_task_return'] & ~1
assert STOCK[0xb31c:0xb32c] == next(data[entry_c-base:entry_c-base+16]
                                     for base, data in segments
                                     if base <= entry_c < base+len(data))
for depth in (0, 1, 0x7fffffff, 0xfffffffe, 0xffffffff):
    pair = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_write(0x2000019c, struct.pack('<I', depth))
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        entry = 0x0800b31c if native else entry_c
        loop_offset = 0x0e if depth == 0xffffffff else 0x0a
        visits = []
        def hook(uc, address, size, user):
            if address == entry + loop_offset:
                visits.append(address-entry)
                if len(visits) == 2:
                    uc.emu_stop()
        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start(entry | 1, 0, count=30)
        pair.append((visits, u.reg_read(UC_ARM_REG_PRIMASK),
                     bytes(u.mem_read(0x2000019c, 4))))
    assert pair[0] == pair[1] == ([loop_offset, loop_offset], 1,
                                  struct.pack('<I', depth)), (depth, pair)
print('PASS_CASE_TASK_RETURN_FAULT', 5, 'depths', 'byte_prefix', 16)
