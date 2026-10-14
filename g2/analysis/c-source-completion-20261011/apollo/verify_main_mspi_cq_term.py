#!/usr/bin/env python3
"""Bounded native/source comparison of Main command queue termination."""
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
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    syms = {s.name: s['st_value'] & ~1
            for s in elf.get_section_by_name('.symtab').iter_symbols()}

QUEUE, OPS, OPTION, CONTROL = 0x20006000, 0x20007000, 0x40060000, 0x40061000
RET = 0x200ff000


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(source, null, magic, force, pending, option, control):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x40060000, 0x2000)
    put(cpu, QUEUE, magic)
    put(cpu, QUEUE + 0x1c, 3 if pending else 4)
    put(cpu, QUEUE + 0x20, 4)
    put(cpu, QUEUE + 0x24, OPS)
    put(cpu, OPS, OPTION)
    put(cpu, OPS + 0x10, CONTROL)
    put(cpu, OPS + 0x14, 0x55aa00ff)
    put(cpu, OPTION, option)
    put(cpu, CONTROL, control)
    cpu.reg_write(R.UC_ARM_REG_R0, 0 if null else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_R1, force)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    events = []
    lower = syms['g2_main_cq_update_indices_538d18'] if source else 0x538d18

    def hook(machine, pc, _size, _user):
        if pc == lower:
            events.append(machine.reg_read(R.UC_ARM_REG_R0))
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((syms['g2_main_cq_term_53909a'] if source else 0x53909a) | 1,
                  RET + 2, count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0), 'events': events,
            'queue': bytes(cpu.mem_read(QUEUE, 0x28)).hex(),
            'option': bytes(cpu.mem_read(OPTION, 4)).hex(),
            'control': bytes(cpu.mem_read(CONTROL, 4)).hex()}


cases = 0
for null, magic, force, pending, option, control in itertools.product(
        (False, True), (0, 0x01cdcdcd, 0x03cdcdcd, 0x01bebebe),
        (0, 1, 256), (False, True), (0, 1, 0xffffffff),
        (0, 0xffffffff)):
    native = run(False, null, magic, force, pending, option, control)
    candidate = run(True, null, magic, force, pending, option, control)
    assert native == candidate, (null, magic, force, pending, option, control,
                                 native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_MSPI_CQ_TERM_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Index-refresh lower is intercepted and synthetic queue/register state is used.',
                     'No physical command queue behavior or complete Main image is verified.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
