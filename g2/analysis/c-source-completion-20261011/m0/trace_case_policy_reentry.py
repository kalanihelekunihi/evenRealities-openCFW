#!/usr/bin/env python3
"""Instruction-backed native 0x7200 policy continuation trace."""
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[4]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
u.mem_map(0x08000000, (len(STOCK)+4095)&~4095)
u.mem_write(0x08000000, STOCK)
u.mem_map(0x20000000, 0x10000)
u.mem_map(0x40007000, 0x1000)
u.mem_map(0xe000e000, 0x1000)
u.mem_write(0x20000888, (17).to_bytes(4, 'little'))
u.reg_write(UC_ARM_REG_SP, 0x20007fe8)
u.reg_write(UC_ARM_REG_LR, 0x20001001)
visits = []
def hook(uc, address, size, user):
    if address in (0x08007214, 0x08007ed6, 0x08007eda,
                   0x0800d154, 0x0800a7b0):
        visits.append((address, uc.reg_read(UC_ARM_REG_SP),
                       uc.reg_read(UC_ARM_REG_LR),
                       int.from_bytes(uc.mem_read(0x20000888, 4), 'little')))
        if address == 0x08007214 and sum(v[0] == address for v in visits) == 3:
            uc.emu_stop()
            return
    if address in (0x0800d154, 0x0800a7b0):
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE, hook)
u.emu_start(0x08007201, 0, count=200000)
assert [v[0] for v in visits if v[0] in (0x08007214,0x08007ed6,0x08007eda)] == [
    0x08007214, 0x08007eda, 0x08007ed6,
    0x08007214, 0x08007eda, 0x08007ed6, 0x08007214], visits
assert [v[1] for v in visits if v[0] == 0x08007214] == [0x20007fc0] * 3, visits
assert [v[2] for v in visits if v[0] == 0x08007214] == [
    0x20001001, 0x08007edb, 0x08007edb], visits
for address, sp, lr, ticks in visits:
    print(f'{address:08x} sp={sp:08x} lr={lr:08x} ticks={ticks}')
print('PASS_CASE_POLICY_REENTRY_TRACE', 3, 'entries')
