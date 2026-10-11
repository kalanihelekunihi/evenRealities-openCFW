#!/usr/bin/env python3
"""Stock/C reset entry 0xb8 boundary check; CRT and application are cut."""
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
rng = random.Random(0xb8)
for index in range(128):
    observations = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.reg_write(UC_ARM_REG_R0, rng.getrandbits(32))
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        crt = 0x08000270 if native else symbols['case_crt_init_0270'] & ~1
        app = 0x0800a598 if native else symbols['case_application_entry_a598'] & ~1
        cuts = []
        def hook(uc, address, size, user):
            if address == crt:
                cuts.append(('crt', uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_SP)))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == app:
                cuts.append(('app', uc.reg_read(UC_ARM_REG_SP)))
                uc.emu_stop()
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x080000b8 if native else symbols['case_startup_entry_00b8'] & ~1
        u.emu_start(entry | 1, 0, count=40)
        observations.append(cuts)
    assert observations[0] == observations[1] == [
        ('crt', 0x20002c88, 0x20002c88), ('app', 0x20002c88)], (index, observations)
print('PASS_CASE_STARTUP_ENTRY_00B8', 128)
