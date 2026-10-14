#!/usr/bin/env python3
"""Locked Main/source comparison for command queue index refresh."""
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

QUEUE, OPS, HEAD, INDEX, RET = 0x20006000, 0x20007000, 0x40060000, 0x40061000, 0x200ff000


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(source, end, index, head, mask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x40060000, 0x2000)
    put(cpu, QUEUE + 0x20, end)
    put(cpu, QUEUE + 0x24, OPS)
    put(cpu, OPS + 4, HEAD)
    put(cpu, OPS + 8, INDEX)
    put(cpu, HEAD, head)
    put(cpu, INDEX, index)
    cpu.reg_write(R.UC_ARM_REG_R0, QUEUE)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    events = []
    helper = syms['g2_main_critical_save_473940'] if source else 0x473940

    def hook(machine, pc, _size, _user):
        if pc == helper:
            events.append('critical_save')
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((syms['g2_main_cq_update_indices_538d18'] if source else 0x538d18) | 1,
                  RET + 2, count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'queue': bytes(cpu.mem_read(QUEUE, 0x28)).hex(),
            'primask': cpu.reg_read(R.UC_ARM_REG_PRIMASK)}


cases = 0
for end, index, head, mask in itertools.product(
        (0, 0xff, 0x100, 0x1ff, 0x200, 0xffffff00, 0xffffffff),
        (0, 1, 0x7f, 0xff, 0x12345678),
        (0, 0x20008000, 0xffffffff), (0, 1)):
    native = run(False, end, index, head, mask)
    candidate = run(True, end, index, head, mask)
    assert native == candidate, (end, index, head, mask, native, candidate)
    cases += 1
for mask in (0, 1):
    outputs = []
    for source in (False, True):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x430000, 0x380000)
        cpu.mem_write(0x437fe0, blob)
        cpu.mem_map(0x800000, 0x10000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x100000)
        cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
        cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
        cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)

        def stop(machine, pc, _size, _user):
            if pc == RET:
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, stop)
        cpu.emu_start((syms['g2_main_critical_save_473940'] if source else 0x473940) | 1,
                      RET + 2, count=100)
        assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
        outputs.append((cpu.reg_read(R.UC_ARM_REG_R0),
                        cpu.reg_read(R.UC_ARM_REG_PRIMASK)))
    assert outputs[0] == outputs[1], (mask, outputs)
    cases += 1
report = {'status': 'PASS_MAIN_MSPI_CQ_INDEX_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Native critical-save is intercepted with a synthetic PRIMASK value; source may inline the same body.',
                     'No physical command queue timing or complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
