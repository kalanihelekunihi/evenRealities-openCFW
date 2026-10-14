#!/usr/bin/env python3
"""Bounded locked-image/source comparison for Main CQ disable."""
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
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    source = next(s['st_value'] & ~1 for s in
                  elf.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'g2_main_cq_disable_538e8c')

QUEUE = 0x20006000
OPS = 0x20007000
REG = 0x40060000
RET = 0x200ff000


def put(cpu, addr, value):
    cpu.mem_write(addr, int(value).to_bytes(4, 'little'))


def run(is_source, null, magic, enabled, initial):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(REG, 0x1000)
    put(cpu, QUEUE, magic | (0x02000000 if enabled else 0))
    put(cpu, QUEUE + 0x24, OPS)
    put(cpu, OPS, REG)
    put(cpu, REG, initial)
    cpu.reg_write(R.UC_ARM_REG_R0, 0 if null else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)

    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x538e8c) | 1, RET + 2,
                  count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'queue': bytes(cpu.mem_read(QUEUE, 0x28)).hex(),
            'register': bytes(cpu.mem_read(REG, 4)).hex()}


count = 0
for null, magic, enabled, initial in itertools.product(
        (False, True), (0, 0x01cdcdcd, 0x03cdcdcd, 0x01bebebe),
        (False, True), (0, 1, 0xffffffff, 0x87654321)):
    a = run(False, null, magic, enabled, initial)
    b = run(True, null, magic, enabled, initial)
    assert a == b, (null, magic, enabled, initial, a, b)
    count += 1
report = {'status': 'PASS_MAIN_MSPI_CQ_DISABLE_BOUNDED_NATIVE_SOURCE',
          'cases': count, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic queue, ops and register state only.',
                     'No physical command queue behavior or complete Main image is verified.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], count)
