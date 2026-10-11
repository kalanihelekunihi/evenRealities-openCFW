#!/usr/bin/env python3
"""Bounded stock/C UART character emission at CASE callback 0xa380."""
from pathlib import Path
import random
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
rng = random.Random(0xa380)
for index in range(256):
    character = rng.getrandbits(32)
    context = rng.getrandbits(32)
    pair = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.reg_write(UC_ARM_REG_R0, character)
        u.reg_write(UC_ARM_REG_R1, context)
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        lower = 0x080066ac if native else symbols['case_write_controller_blocking'] & ~1
        calls = []
        def hook(uc, address, size, user):
            if address != lower:
                return
            ptr = uc.reg_read(UC_ARM_REG_R1)
            calls.append((uc.reg_read(UC_ARM_REG_R0),
                          bytes(uc.mem_read(ptr, 1)),
                          uc.reg_read(UC_ARM_REG_R2),
                          uc.reg_read(UC_ARM_REG_R3)))
            uc.reg_write(UC_ARM_REG_R0, rng.getrandbits(32))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x0800a380 if native else symbols['case_log_output_char'] & ~1
        u.emu_start(entry | 1, 0x20009000, count=60)
        pair.append((calls, u.reg_read(UC_ARM_REG_R0)))
    expected = ([(0x20000e24, bytes((character & 0xff,)), 1, 0xffff)], character)
    assert pair[0] == pair[1] == expected, (index, pair, expected)
print('PASS_CASE_LOG_OUTPUT_CHAR', 256)
