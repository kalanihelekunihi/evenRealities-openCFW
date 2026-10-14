#!/usr/bin/env python3
"""Compare bounded Main MSPI CQ wrapper effects with the locked image."""
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
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
with args.elf.open('rb') as handle:
    elf = ELFFile(handle)
    segments = [(seg['p_vaddr'], seg.data()) for seg in elf.iter_segments()
                if seg['p_type'] == 'PT_LOAD' and seg['p_filesz']]
    syms = {s.name: s['st_value'] & ~1
            for s in elf.get_section_by_name('.symtab').iter_symbols()}

NATIVE = {'init': 0x4bfc5a, 'disable': 0x4bfd62, 'term': 0x4bfc86}
SOURCE = {name: syms['g2_main_mspi_cq_' + name + '_' + format(addr, 'x')]
          for name, addr in NATIVE.items()}
LOWER_NATIVE = {0x538d58: 'init', 0x538e8c: 'disable', 0x53909a: 'term'}
LOWER_SOURCE = {syms['g2_main_cq_' + name + '_' + format(addr, 'x')]: name
                for addr, name in LOWER_NATIVE.items()}
STATE = 0x20006000
SLOT = 0x200523d8 + 0x828
QUEUE = 0x20008000
RET = 0x200ff000
SP = 0x200fe000


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(name, is_source, module, size, buffer, queue, status):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(STATE, bytes([0xa5]) * 0x8d0)
    put(cpu, STATE + 4, module)
    put(cpu, STATE + 0x828, queue)
    put(cpu, SLOT + module * 0x8d0, queue)
    cpu.reg_write(R.UC_ARM_REG_SP, SP)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    for reg, value in ((R.UC_ARM_REG_R0, module if name == 'init' else STATE),
                       (R.UC_ARM_REG_R1, size), (R.UC_ARM_REG_R2, buffer)):
        cpu.reg_write(reg, value)
    events = []

    def hook(machine, pc, _length, _user):
        if pc in (LOWER_SOURCE if is_source else LOWER_NATIVE):
            lower = (LOWER_SOURCE if is_source else LOWER_NATIVE)[pc]
            r0, r1, r2 = (machine.reg_read(reg) for reg in
                          (R.UC_ARM_REG_R0, R.UC_ARM_REG_R1, R.UC_ARM_REG_R2))
            if lower == 'init':
                config = bytes(machine.mem_read(r1, 9)).hex()
                events.append([lower, r0, config, r2])
            elif lower == 'term':
                events.append([lower, r0, r1])
            else:
                events.append([lower, r0])
            machine.reg_write(R.UC_ARM_REG_R0, status)
            machine.reg_write(R.UC_ARM_REG_PC,
                              machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((SOURCE if is_source else NATIVE)[name] | 1, RET + 2,
                  count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0), 'events': events,
            'slot': bytes(cpu.mem_read(SLOT + module * 0x8d0, 4)).hex(),
            'state_slot': bytes(cpu.mem_read(STATE + 0x828, 4)).hex()}


cases = 0
for name, module, size, buffer, queue, status in itertools.product(
        NATIVE, (0, 1, 2), (0, 7, 256), (0, QUEUE), (0, QUEUE), (0, 7)):
    native = run(name, False, module, size, buffer, queue, status)
    source = run(name, True, module, size, buffer, queue, status)
    # The C init API is void; caller behavior cannot depend on residual R0.
    if name == 'init':
        native.pop('r0')
        source.pop('r0')
    assert native == source, (name, module, size, buffer, queue, status,
                              native, source)
    cases += 1

report = {'status': 'PASS_MAIN_MSPI_CQ_WRAPPERS_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Provider calls are intercepted; only wrapper arguments and SRAM effects are compared.',
                     'No hardware command queue, timing or complete Main image is verified.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
