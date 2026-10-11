#!/usr/bin/env python3
"""Bounded whole-callback state/call comparison for indirect CASE 0xbb90."""
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

native_targets = {0x08003848: 'hall', 0x0800aaf0: 'event',
                  0x0800ab26: 'reset', 0x0800a888: 'finish',
                  0x08009170: 'log'}
source_targets = {symbols[name] & ~1: kind for name, kind in (
    ('case_boot_irq_hall_prepare', 'hall'),
    ('case_policy_event_signal', 'event'),
    ('case_policy_task_reset', 'reset'),
    ('case_boot_sensor_finish_signal', 'finish'),
    ('case_policy_log', 'log'), ('case_policy_log_four', 'log'))}
rng = random.Random(0xbb90)
for index in range(256):
    state = bytearray(0x70)
    shared = bytearray(0x50)
    state[0] = rng.randrange(5)
    state[2] = rng.randrange(6)
    state[16] = rng.randrange(2)
    state[17] = rng.randrange(2)
    state[48] = rng.randrange(2)
    state[52] = rng.randrange(2)
    state[76] = rng.randrange(2)
    state[80] = rng.randrange(2)
    struct.pack_into('<I', state, 68, rng.choice((0, 1, 209, 210, 211)))
    struct.pack_into('<I', state, 96, rng.choice((0, 1, 209, 210, 211)))
    shared[7] = rng.randrange(2)
    for offset in (16, 24, 56):
        struct.pack_into('<I', shared, offset, 0x20003000 + rng.randrange(100) * 4)
    results = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_write(0x2000087c, bytes(state))
        u.mem_write(0x200000b8, bytes(shared))
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        calls = []
        targets = native_targets if native else source_targets
        def hook(uc, address, size, user):
            if address in targets:
                kind = targets[address]
                calls.append((kind, uc.reg_read(UC_ARM_REG_R0),
                              None if kind == 'log' else uc.reg_read(UC_ARM_REG_R1)))
                uc.reg_write(UC_ARM_REG_R0, 0x12345678)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x0800bb90 if native else symbols['case_boot_transport_cb_bb90'] & ~1
        u.emu_start(entry | 1, 0x20009000, count=4000)
        results.append((calls, bytes(u.mem_read(0x2000087c, 0x70)),
                        bytes(u.mem_read(0x200000b8, 0x50))))
    assert results[0] == results[1], (index, results[0][0], results[1][0],
                                      list(state), list(shared))
print('PASS_CASE_TRANSPORT_CB_BB90', 256)
