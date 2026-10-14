#!/usr/bin/env python3
"""Bounded Main CQ initializer and source-owned resource table oracle."""
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

NATIVE_TABLE = 0x6c0f40
SOURCE_TABLE = syms['g2_main_cmdq_resources']
table = next(data[SOURCE_TABLE - address:SOURCE_TABLE - address + 480]
             for address, data in segments
             if address <= SOURCE_TABLE < address + len(data))
assert len(table) == 480
assert table == blob[NATIVE_TABLE - 0x437fe0:NATIVE_TABLE - 0x437fe0 + 480]
STATE, CONFIG, SLOT, RET = 0x2006ef28, 0x20008100, 0x20008000, 0x200ff000
MMIO = 0x40050000
registers = sorted({int.from_bytes(table[row * 40 + offset:row * 40 + offset + 4], 'little')
                    for row in range(12) for offset in (0, 4, 8, 12, 16)})


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(source, interface, config_present, size, buffer, slot_present, busy, option):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x14000)
    cpu.mem_write(STATE, bytes([0xa5]) * (12 * 44))
    for row in range(12):
        put(cpu, STATE + row * 44, 0x02000000 | (0x01000000 if busy else 0))
    for address in registers:
        put(cpu, address, 0xa5a5a5a5)
    put(cpu, CONFIG, size)
    put(cpu, CONFIG + 4, buffer)
    cpu.mem_write(CONFIG + 8, bytes([option]))
    put(cpu, SLOT, 0x12345678)
    cpu.reg_write(R.UC_ARM_REG_R0, interface)
    cpu.reg_write(R.UC_ARM_REG_R1, CONFIG if config_present else 0)
    cpu.reg_write(R.UC_ARM_REG_R2, SLOT if slot_present else 0)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)

    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((syms['g2_main_cq_init_538d58'] if source else 0x538d58) | 1,
                  RET + 2, count=2000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    states = bytearray(cpu.mem_read(STATE, 12 * 44))
    if source:
        for row in range(12):
            offset = row * 44 + 0x24
            ptr = int.from_bytes(states[offset:offset + 4], 'little')
            if SOURCE_TABLE <= ptr < SOURCE_TABLE + 480:
                states[offset:offset + 4] = (NATIVE_TABLE + ptr - SOURCE_TABLE).to_bytes(4, 'little')
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'states': states.hex(), 'slot': bytes(cpu.mem_read(SLOT, 4)).hex(),
            'registers': [bytes(cpu.mem_read(address, 4)).hex()
                          for address in registers]}


cases = 0
for interface, config_present, size, buffer, slot_present, busy, option in itertools.product(
        (0, 1, 7, 8, 11, 12, 255, 256), (False, True),
        (0, 1, 2, 0x100), (0, 0x20008000),
        (False, True), (False, True), (0, 1, 2)):
    native = run(False, interface, config_present, size, buffer,
                 slot_present, busy, option)
    candidate = run(True, interface, config_present, size, buffer,
                    slot_present, busy, option)
    assert native == candidate, (interface, config_present, size, buffer,
                                 slot_present, busy, option, native, candidate)
    cases += 1

report = {'status': 'PASS_MAIN_MSPI_CQ_INIT_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'resource_table_sha256': hashlib.sha256(table).hexdigest(),
          'resource_rows': 12,
          'limits': ['Synthetic MMIO and SRAM; source table pointers are normalized to stock placement for comparison.',
                     'No physical command queue operation or complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
