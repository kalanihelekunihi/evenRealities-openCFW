#!/usr/bin/env python3
"""Compare Main NOR clock-selector request order against locked instructions."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as R

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == STOCK_SHA
p = argparse.ArgumentParser()
p.add_argument('--elf', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.elf.open('rb') as f:
    elf = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    syms = {s.name: s['st_value'] & ~1
            for s in elf.get_section_by_name('.symtab').iter_symbols()}

RET = 0x200ff000


def run(source, controller, mode):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    for address in range(0x20000138, 0x200001b0, 4):
        cpu.mem_write(address, (address ^ 0x5a5a5a5a).to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, controller)
    cpu.reg_write(R.UC_ARM_REG_R1, mode)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    events = []
    lower = syms['g2_main_clock_request_480f0c'] if source else 0x480f0c

    def hook(machine, pc, _size, _user):
        if pc == lower:
            events.append([machine.reg_read(R.UC_ARM_REG_R0),
                           machine.reg_read(R.UC_ARM_REG_R1)])
            machine.reg_write(R.UC_ARM_REG_R0, 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((syms['g2_norflash_clock_select_4c32b4'] if source else 0x4c32b4) | 1,
                  RET + 2, count=2000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return events


cases = 0
for controller, mode in itertools.product((0, 1, 2, 3, 4, 0x100), range(256)):
    native = run(False, controller, mode)
    candidate = run(True, controller, mode)
    assert native == candidate, (controller, mode, native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_NOR_CLOCK_SELECT_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Clock request lower is intercepted; only request ID, value and order are compared.',
                     'SRAM clock words are seeded synthetic values; their initialization and physical clock behavior are unverified.',
                     'No complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
