#!/usr/bin/env python3
"""Bounded stock/C call ABI checks for indirect timer callbacks."""
from pathlib import Path
import random
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
ELF = HERE / 'case_absolute_experiment.elf'
with ELF.open('rb') as stream:
    image = ELFFile(stream)
    symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
    segments = [(p['p_vaddr'], p.data()) for p in image.iter_segments() if p['p_type'] == 'PT_LOAD']

callbacks = (
    (0x0800bf84, 0x0800c44c, 'vEventGroupClearBitsCallback', 'xEventGroupClearBits'),
    (0x0800bf8c, 0x0800c4de, 'vEventGroupSetBitsCallback', 'xEventGroupSetBits'),
)
for _, _, callback, lower in callbacks:
    assert callback in symbols and lower in symbols
rng = random.Random(0xbf8c)
for i in range(256):
    event = 0x20000000 + 4 * rng.randrange(0x100)
    bits = rng.getrandbits(32)
    results = []
    entry_native, target_native, entry_source, target_source = callbacks[i % 2]
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.mem_map(0x08000000, 0x20000)
        u.mem_write(0x08000000, STOCK)
        u.mem_map(0x00100000, 0x10000)
        if not native:
            for address, data in segments:
                u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.reg_write(UC_ARM_REG_R0, event)
        u.reg_write(UC_ARM_REG_R1, bits)
        u.reg_write(UC_ARM_REG_SP, 0x20008000)
        u.reg_write(UC_ARM_REG_LR, 0x20009001)
        target = target_native if native else symbols[target_source] & ~1
        calls = []
        def hook(uc, address, size, user):
            if address == target:
                calls.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
                uc.emu_stop()
        u.hook_add(UC_HOOK_CODE, hook)
        entry = entry_native if native else symbols[entry_source] & ~1
        u.emu_start(entry | 1, 0, count=24)
        results.append(calls)
    assert results[0] == results[1] == [(event, bits)], (i, results)
print('PASS_CASE_EVENT_TIMER_CALLBACK_ABI', 256)
