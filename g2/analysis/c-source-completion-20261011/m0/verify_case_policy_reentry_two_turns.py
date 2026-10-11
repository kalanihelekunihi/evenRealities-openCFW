#!/usr/bin/env python3
"""Stock/C 0x7200 policy entry through two completed 0x7214 turns."""
from pathlib import Path
import itertools, os, subprocess, sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
# The established iteration builder links only policy sources and cut lowers.
subprocess.run([sys.executable, str(HERE / 'verify_case_policy_iteration.py')],
               check=True, capture_output=True)
with (HERE / 'policy_iteration_oracle.elf').open('rb') as stream:
    image = ELFFile(stream)
    symbols = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}
    segments = [(p['p_vaddr'], p.data()) for p in image.iter_segments() if p['p_type'] == 'PT_LOAD']

checked = 0
turns = int(os.environ.get('CASE_POLICY_TURNS', '3'))
assert 3 <= turns <= 65
for seconds, left, right in itertools.product((0, 4), (0, 1), (0, 1)):
    pair = []
    for native in (True, False):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
        u.mem_map(0x08000000, (len(STOCK)+4095)&~4095)
        u.mem_write(0x08000000, STOCK)
        u.mem_map(0x00100000, 0x200000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_map(0x40007000, 0x1000)
        u.mem_map(0xe000e000, 0x1000)
        u.mem_write(0x20000884, seconds.to_bytes(4, 'little'))
        u.mem_write(0x20000888, (17).to_bytes(4, 'little'))
        u.mem_write(0x2000087f, bytes((left,)))
        u.mem_write(0x20000880, bytes((right,)))
        u.reg_write(UC_ARM_REG_SP, 0x20007fe8)
        u.reg_write(UC_ARM_REG_LR, 0x20001001)
        entries = []
        calls = []
        turn = 0x08007214 if native else symbols['case_policy_task_iteration_7214'] & ~1
        lower = ({0x0800d154: 'service_idle', 0x0800a7b0: 'wait'} if native else
                 {symbols['case_policy_service_idle'] & ~1: 'service_idle',
                  symbols['case_policy_wait'] & ~1: 'wait'})
        def hook(uc, address, size, user):
            if address == turn:
                entries.append((uc.reg_read(UC_ARM_REG_SP), uc.reg_read(UC_ARM_REG_LR)))
                if len(entries) == turns:
                    uc.emu_stop()
                    return
            kind = lower.get(address)
            if kind:
                calls.append((kind, uc.reg_read(UC_ARM_REG_R0) if kind == 'wait' else 0))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        entry = 0x08007200 if native else symbols['case_policy_task_7200'] & ~1
        try:
            u.emu_start(entry | 1, 0, count=200000)
        except Exception as exc:
            raise AssertionError((seconds, left, right, native,
                                  hex(u.reg_read(UC_ARM_REG_PC)),
                                  hex(u.reg_read(UC_ARM_REG_R0)), calls)) from exc
        assert len(entries) == turns, (seconds, left, right, native,
                                       hex(u.reg_read(UC_ARM_REG_PC)), entries, calls)
        pair.append((calls, bytes(u.mem_read(0x2000087c, 0x64)),
                     int.from_bytes(u.mem_read(0x20000888, 4), 'little'), entries))
    assert pair[0][:3] == pair[1][:3], (seconds, left, right, pair[0], pair[1])
    assert [sp for sp, _ in pair[0][3]] == [0x20007fc0] * turns
    assert [lr for _, lr in pair[0][3]] == [0x20001001] + [0x08007edb] * (turns-1)
    assert len({sp for sp, _ in pair[1][3]}) == 1, pair[1][3]
    assert pair[1][3][1][1] == pair[1][3][2][1], pair[1][3]
    checked += 1
print('PASS_CASE_POLICY_REENTRY_TURNS', checked, turns)
