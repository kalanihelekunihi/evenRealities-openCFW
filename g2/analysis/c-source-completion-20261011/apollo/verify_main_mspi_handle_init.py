#!/usr/bin/env python3
"""Bounded native/source comparison for Main MSPI handle initialization."""
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
    source = next(s['st_value'] & ~1 for s in
                  elf.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'g2_main_mspi_handle_init_4c0812')

STATE = 0x200523d8
SLOTS = (0, 0x20074544, 0x20008000)
RET = 0x200ff000


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(is_source, module, slot, flags):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(STATE, bytes([0xa5]) * (4 * 0x8d0))
    for row in range(4):
        put(cpu, STATE + row * 0x8d0, flags)
    for address in SLOTS[1:]:
        put(cpu, address, 0x12345678)
    cpu.reg_write(R.UC_ARM_REG_R0, module)
    cpu.reg_write(R.UC_ARM_REG_R1, slot)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)

    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x4c0812) | 1,
                  RET + 2, count=1000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'states': bytes(cpu.mem_read(STATE, 4 * 0x8d0)).hex(),
            'slots': [bytes(cpu.mem_read(address, 4)).hex()
                      for address in SLOTS[1:]]}


cases = 0
for module, slot, flags in itertools.product(
        (0, 1, 2, 3, 4, 0xffffffff), SLOTS,
        (0, 0x02000000, 0x01000000, 0x80000000, 0x82000000)):
    native = run(False, module, slot, flags)
    candidate = run(True, module, slot, flags)
    assert native == candidate, (module, slot, flags, native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_MSPI_HANDLE_INIT_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic SRAM state and output slot; includes the fixed NOR controller word.',
                     'The broader caller at 0x46fb0c and physical MSPI setup are not source complete.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
