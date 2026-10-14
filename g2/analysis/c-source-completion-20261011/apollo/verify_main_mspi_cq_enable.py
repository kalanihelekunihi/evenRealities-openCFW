#!/usr/bin/env python3
"""Bounded native/source comparison for Main CQ enable."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as R

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == STOCK_SHA
p = argparse.ArgumentParser()
p.add_argument('--elf', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.elf.open('rb') as f:
    elf = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    source = next(s['st_value'] & ~1 for s in
                  elf.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'g2_main_cq_enable_538e3c')

QUEUE, OPS, OPTION, RET = 0x20006000, 0x20007000, 0x40060000, 0x200ff000


def put(cpu, addr, value):
    cpu.mem_write(addr, int(value).to_bytes(4, 'little'))


def run(is_source, null, magic, enabled, read_pointer, initial):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(OPTION, 0x1000)
    put(cpu, QUEUE, magic | (0x02000000 if enabled else 0))
    put(cpu, QUEUE + 8, read_pointer)
    put(cpu, QUEUE + 0x24, OPS)
    put(cpu, OPS, OPTION)
    put(cpu, OPTION, initial)
    cpu.reg_write(R.UC_ARM_REG_R0, 0 if null else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)

    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x538e3c) | 1,
                  RET + 2, count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'queue': bytes(cpu.mem_read(QUEUE, 0x28)).hex(),
            'option': bytes(cpu.mem_read(OPTION, 4)).hex()}


cases = 0
for null, magic, enabled, read_pointer, initial in itertools.product(
        (False, True), (0, 0x01cdcdcd, 0x03cdcdcd, 0x01bebebe),
        (False, True),
        (0, 0x2007ffff, 0x20080000, 0xffffffff),
        (0, 1, 0xffffffff, 0x87654320)):
    native = run(False, null, magic, enabled, read_pointer, initial)
    candidate = run(True, null, magic, enabled, read_pointer, initial)
    assert native == candidate, (null, magic, enabled, read_pointer, initial,
                                 native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_MSPI_CQ_ENABLE_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic queue and option register state only.',
                     'A memory barrier instruction is present in source, but physical ordering is unverified.',
                     'No complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
