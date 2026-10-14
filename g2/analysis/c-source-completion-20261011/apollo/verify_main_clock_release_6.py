#!/usr/bin/env python3
"""Locked Main/source class 6 release and queue-disable comparison."""
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
TABLE, QUEUE, MMIO, RET = 0x20073324, 0x20008000, 0x40020000, 0x200ff000
NATIVE_HELPERS = {0x473940: 'critical', 0x539944: 'uninit',
                  0x4c3e9a: 'release2', 0x4c3d28: 'release3'}
SOURCE_HELPERS = {syms['g2_main_critical_save_473940']: 'critical',
                  syms['g2_main_queue_uninit_539944']: 'uninit',
                  syms['g2_main_clock_release_2_4c3e9a']: 'release2',
                  syms['g2_main_clock_release_3_4c3d28']: 'release3'}

def run(source, direct, requested, other, mode, valid_queue, mask, high, pattern):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x2000)
    cpu.mem_write(TABLE, bytes(56))
    if requested:
        cpu.mem_write(TABLE + 48, (1 << 11).to_bytes(4, 'little'))
    if other:
        old = int.from_bytes(cpu.mem_read(TABLE + 48, 4), 'little')
        cpu.mem_write(TABLE + 48, (old | 1).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE, (0x01504c30 if valid_queue else 0).to_bytes(4, 'little'))
    cpu.mem_write(0x2007425c, QUEUE.to_bytes(4, 'little'))
    cpu.mem_write(0x20074f5b, b'\x01')
    cpu.mem_write(0x20073f48, bytes([mode]))
    cpu.reg_write(R.UC_ARM_REG_R0, QUEUE if direct else 11)
    cpu.reg_write(R.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(R.UC_ARM_REG_R2, high)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    events = []
    helpers = SOURCE_HELPERS if source else NATIVE_HELPERS
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc in helpers:
            event = helpers[pc]
            events.append((event, machine.reg_read(R.UC_ARM_REG_R0) if event != 'critical' else None))
            if event == 'critical':
                machine.reg_write(R.UC_ARM_REG_R0, mask)
                machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            else:
                machine.reg_write(R.UC_ARM_REG_R0, 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_queue_disable_539a10'] if direct else
             syms['g2_main_clock_release_6_4c43ec']) if source else (0x539a10 if direct else 0x4c43ec)
    cpu.emu_start(entry | 1, RET + 2, count=5000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            None if direct else cpu.reg_read(R.UC_ARM_REG_R1),
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(TABLE, 56)), bytes(cpu.mem_read(MMIO, 0x2000)),
            bytes(cpu.mem_read(QUEUE, 4)),
            bytes(cpu.mem_read(0x2007425c, 4)),
            bytes(cpu.mem_read(0x20074f5b, 1)))

fixtures = list(itertools.product((False, True), (False, True),
                                  (0, 1), (False, True), (0, 1),
                                  (0, 0x12345678), (0, 0xa5)))
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture)
    candidate = run(True, False, *fixture)
    if native != candidate:
        raise AssertionError(('release', index, fixture, native[:5], candidate[:5], native[6:], candidate[6:]))
for index, (valid, pattern) in enumerate(itertools.product((False, True), (0, 0xa5))):
    fixture = (False, False, 0, valid, 0, 0, pattern)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('disable', index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_CLOCK_RELEASE_6_QUEUE_DISABLE_NATIVE_SOURCE',
          'cases': len(fixtures) + 4, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical save, queue uninitialization and downstream class 2/3 releases intercepted.',
                     'Queue disable and request bitmap executed against synthetic MMIO/SRAM.',
                     'Physical operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 4)
