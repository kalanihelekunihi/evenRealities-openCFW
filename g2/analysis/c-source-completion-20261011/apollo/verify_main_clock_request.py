#!/usr/bin/env python3
"""Bounded locked Main/source comparison for clock request and mask tables."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
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


def source_bytes(address, size):
    return next(data[address - base:address - base + size]
                for base, data in segments if base <= address < base + len(data))


type_mask = source_bytes(syms['g2_main_clock_type_mask'], 28)
second_mask = source_bytes(syms['g2_main_clock_secondary_mask'], 28)
assert type_mask == blob[0x768ba8 - 0x437fe0:0x768ba8 - 0x437fe0 + 28]
assert second_mask == blob[0x768bc4 - 0x437fe0:0x768bc4 - 0x437fe0 + 28]
MMIO, RET = 0x40010000, 0x200ff000


def run(source, clock_id, value, mask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x1000)
    cpu.mem_write(MMIO, bytes([0xa5]) * 0x404)
    cpu.reg_write(R.UC_ARM_REG_R0, clock_id)
    cpu.reg_write(R.UC_ARM_REG_R1, value)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    events = []
    helper = syms['g2_main_critical_save_473940'] if source else 0x473940

    def code_hook(machine, pc, _size, _user):
        if pc == helper:
            events.append(['critical_save', mask])
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()

    def write_hook(_machine, _access, address, size, written, _user):
        if MMIO <= address < MMIO + 0x404:
            events.append(['write', address, size, written & 0xffffffff])

    cpu.hook_add(UC_HOOK_CODE, code_hook)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    cpu.emu_start((syms['g2_main_clock_request_480f0c'] if source else 0x480f0c) | 1,
                  RET + 2, count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'primask': cpu.reg_read(R.UC_ARM_REG_PRIMASK),
            'events': events,
            'registers': bytes(cpu.mem_read(MMIO, 0x404)).hex()}


values = (0, 0x400, 0x800, 0xc00, 0x2000, 0x4000, 0xc000, 0xffffffff)
cases = 0
for clock_id, value, mask in itertools.product(
        (*range(0xe0), 0xe0, 0xff, 0x100), values, (0, 1)):
    native = run(False, clock_id, value, mask)
    candidate = run(True, clock_id, value, mask)
    assert native == candidate, (clock_id, value, mask, native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_CLOCK_REQUEST_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'type_mask_sha256': hashlib.sha256(type_mask).hexdigest(),
          'secondary_mask_sha256': hashlib.sha256(second_mask).hexdigest(),
          'limits': ['Critical-save is intercepted with synthetic PRIMASK; MMIO write order and final state are compared.',
                     'Physical clock operation and complete Main image are unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
