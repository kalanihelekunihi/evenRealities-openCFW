#!/usr/bin/env python3
"""Compare the only native formatter caller's AAPCS varargs handoff."""
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

rng = random.Random(0x9170)
for index in range(128):
    words = [rng.getrandbits(32) for _ in range(5)]
    observations = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        sp = 0x20008000
        u.mem_write(sp, struct.pack('<2I', *words[3:]))
        for register, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                                   (0x20002000, *words[:3])):
            u.reg_write(register, value)
        u.reg_write(UC_ARM_REG_SP, sp)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        target = 0x08009210 if native else symbols['case_vformat'] & ~1
        got = []
        def hook(uc, address, size, user):
            if address == target:
                arg = uc.reg_read(UC_ARM_REG_R1)
                got.append((uc.reg_read(UC_ARM_REG_R0),
                            struct.unpack('<5I', bytes(uc.mem_read(arg, 20))),
                            uc.reg_read(UC_ARM_REG_R2),
                            uc.reg_read(UC_ARM_REG_R3)))
                uc.emu_stop()
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x08009170 if native else symbols['g2_log_printf'] & ~1
        u.emu_start(entry | 1, 0, count=80)
        assert len(got) == 1, (index, native, got)
        observations.append(got[0])
    original, candidate = observations
    assert original[:3] == candidate[:3] == (0x20002000, tuple(words), 0x200001a0), (index, observations)
    assert original[3] == 0x0800a381, (index, observations)
    assert candidate[3] == symbols['case_log_output_char'], (index, observations)
print('PASS_CASE_LOGGER_CONSUMER_ABI', 128)
