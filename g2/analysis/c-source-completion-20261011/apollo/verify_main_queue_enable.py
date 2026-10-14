#!/usr/bin/env python3
"""Locked Main/source queue enable readiness comparison."""
import argparse, hashlib, itertools, json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as R

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == SHA
p = argparse.ArgumentParser()
p.add_argument('--elf', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.elf.open('rb') as f:
    elf = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    source = next(s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'g2_main_queue_enable_539994')
QUEUE, MMIO, RET = 0x20008000, 0x40020000, 0x200ff000

def run(is_source, present, valid, active, ready_bits, control):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(QUEUE, ((0x01504c30 if valid else 0) |
                          (0x02000000 if active else 0)).to_bytes(4, 'little'))
    cpu.mem_write(0x40020060, (ready_bits << 16).to_bytes(4, 'little'))
    cpu.mem_write(0x400204d8, control.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, QUEUE if present else 0)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x539994) | 1, RET + 2, count=3000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), bytes(cpu.mem_read(QUEUE, 4)),
            bytes(cpu.mem_read(MMIO, 0x2000)))

fixtures = list(itertools.product((False, True), (False, True), (False, True),
                                  range(16), (0, 0xa5a5a5a5, 0xffffffff)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        raise AssertionError((index, fixture, native[:2], candidate[:2]))
report = {'status': 'PASS_MAIN_QUEUE_ENABLE_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic queue handle and MMIO readiness bits only.',
                     'Physical queue operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
