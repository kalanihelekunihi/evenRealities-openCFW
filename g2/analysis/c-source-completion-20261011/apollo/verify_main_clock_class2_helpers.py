#!/usr/bin/env python3
"""Locked Main/source class 2 mode and timeout helper comparison."""
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
    syms = {s.name: s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
SLOT, RET = 0x20009000, 0x200ff000

def run(source, mode_read, control, active, remaining, low, high, mask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x40020000, 0x2000)
    cpu.mem_write(0x4002012c, control.to_bytes(4, 'little'))
    cpu.mem_write(0x20074f56, bytes([active]))
    cpu.mem_write(0x20074260, (SLOT).to_bytes(4, 'little'))
    cpu.mem_write(SLOT, remaining.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, SLOT)
    cpu.reg_write(R.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(R.UC_ARM_REG_R2, low)
    cpu.reg_write(R.UC_ARM_REG_R3, high)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    critical = syms['g2_main_critical_save_473940'] if source else 0x473940
    wait = syms['g2_main_clock_timeout_wait_4c387e'] if source else 0x4c387e
    events = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == critical:
            events.append(('critical',))
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == wait:
            events.append(('wait', machine.reg_read(R.UC_ARM_REG_R0),
                           machine.reg_read(R.UC_ARM_REG_R1)))
            machine.reg_write(R.UC_ARM_REG_R0, 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_clock_mode_read_480c56'] if mode_read else
             syms['g2_main_clock_timeout_cleanup_4c3d70']) if source else (0x480c56 if mode_read else 0x4c3d70)
    cpu.emu_start(entry | 1, RET + 2, count=4000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            cpu.reg_read(R.UC_ARM_REG_R1) if not mode_read else None,
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(SLOT, 4)),
            bytes(cpu.mem_read(0x20074f56, 1)),
            bytes(cpu.mem_read(0x20074260, 4)))

fixtures = list(itertools.product((0, 1, 0x100, 0x101, 0xffffffff),
                                  (0, 1), (0, 1, 3), (0, 0x12345678),
                                  (0, 0x87654321), (0, 1)))
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture)
    candidate = run(True, False, *fixture)
    if native != candidate:
        raise AssertionError(('cleanup', index, fixture, native, candidate))
for index, control in enumerate((0, 1, 0x100, 0x101, 0xffffffff)):
    fixture = (control, 0, 0, 0, 0, 0)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('mode', index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_CLOCK_CLASS2_HELPERS_NATIVE_SOURCE',
          'cases': len(fixtures) + 5, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical save and timeout wait intercepted; mode read and state cleanup executed.',
                     'Synthetic SRAM/MMIO only; physical clock transition and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 5)
