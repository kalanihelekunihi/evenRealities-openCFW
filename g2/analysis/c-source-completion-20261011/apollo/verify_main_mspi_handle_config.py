#!/usr/bin/env python3
"""Bounded native/source Main MSPI handle configuration comparison."""
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
                  if s.name == 'g2_main_mspi_handle_config_4c08a8')

STATE, OTHER, CONFIG, MMIO, RET = 0x200523d8, 0x20006000, 0x20008000, 0x40060000, 0x200ff000


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def run(is_source, module, alias, flags, length, buffer, original_buffer, byte8):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x4000)
    cpu.mem_write(STATE, bytes([0xa5]) * (4 * 0x8d0))
    cpu.mem_write(OTHER, bytes([0xa5]) * 0x8d0)
    cpu.mem_write(MMIO, bytes([0xa5]) * 0x4000)
    handle = STATE + module * 0x8d0 if alias else OTHER
    put(cpu, handle, flags)
    put(cpu, handle + 4, module)
    put(cpu, handle + 0x14, length)
    put(cpu, handle + 0x18, original_buffer)
    cpu.mem_write(CONFIG, bytes([0xcc]) * 12)
    put(cpu, CONFIG, length)
    put(cpu, CONFIG + 4, buffer)
    cpu.mem_write(CONFIG + 8, bytes([byte8]))
    cpu.reg_write(R.UC_ARM_REG_R0, handle)
    cpu.reg_write(R.UC_ARM_REG_R1, CONFIG)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)

    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x4c08a8) | 1,
                  RET + 2, count=2000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0),
            'states': bytes(cpu.mem_read(STATE, 4 * 0x8d0)).hex(),
            'other': bytes(cpu.mem_read(OTHER, 0x8d0)).hex(),
            'mmio': bytes(cpu.mem_read(MMIO, 0x4000)).hex()}


cases = 0
for module, alias, flags, length, buffer, original_buffer, byte8 in itertools.product(
        (0, 1, 3), (False, True),
        (0, 0x01bebebe, 0x03bebebe),
        (0, 8, 0x100), (0, 0x20008000),
        (0, 0x20008000), (0, 0x7f)):
    native = run(False, module, alias, flags, length, buffer,
                 original_buffer, byte8)
    candidate = run(True, module, alias, flags, length, buffer,
                    original_buffer, byte8)
    assert native == candidate, (module, alias, flags, length, buffer,
                                 original_buffer, byte8, native, candidate)
    cases += 1
report = {'status': 'PASS_MAIN_MSPI_HANDLE_CONFIG_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic MMIO and SRAM; both aliased and separate handle/state addresses are compared.',
                     'Null handle/configuration is excluded because the native body dereferences them before validation.',
                     'No physical MSPI setup or complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], cases)
