#!/usr/bin/env python3
"""Locked Main/source queue uninitialization and IRQ-state comparison."""
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
QUEUE, OUTPUT, MMIO, RET = 0x20008000, 0x20009000, 0x40020000, 0x200ff000

def run(source, direct, valid, active, irq_disabled, pattern, high, present):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x2000)
    control = int.from_bytes(cpu.mem_read(0x400204d8, 4), 'little')
    cpu.mem_write(0x400204d8, ((control & 0x7fffffff) |
                                   (0x80000000 if irq_disabled else 0)).to_bytes(4, 'little'))
    queue_word = (0x01504c30 if valid else 0) | (0x02000000 if active else 0)
    cpu.mem_write(QUEUE, queue_word.to_bytes(4, 'little'))
    cpu.mem_write(OUTPUT, b'\xa5\xa5\xa5\xa5')
    cpu.reg_write(R.UC_ARM_REG_R0, OUTPUT if direct else (QUEUE if present else 0))
    cpu.reg_write(R.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(R.UC_ARM_REG_R2, 0x87654321)
    cpu.reg_write(R.UC_ARM_REG_R3, high)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    irq_enable = syms['g2_main_irq_enable_48009e'] if source else 0x48009e
    events = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == irq_enable:
            events.append('irq_enable')
            machine.reg_write(R.UC_ARM_REG_R0, 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_irq_enabled_4800e4'] if direct else
             syms['g2_main_queue_uninit_539944']) if source else (0x4800e4 if direct else 0x539944)
    cpu.emu_start(entry | 1, RET + 2, count=5000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            None if direct else cpu.reg_read(R.UC_ARM_REG_R1), events,
            bytes(cpu.mem_read(QUEUE, 4)), bytes(cpu.mem_read(OUTPUT, 4)),
            bytes(cpu.mem_read(MMIO, 0x2000)))

fixtures = list(itertools.product((False, True), (False, True), (False, True),
                                  (0, 0xa5), (0, 0x12345678), (False, True)))
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture)
    candidate = run(True, False, *fixture)
    if native != candidate:
        differences = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[5], candidate[5])) if x != y]
        raise AssertionError(('uninit', index, fixture, native[:5], candidate[:5], differences[:12]))
for index, (irq_disabled, pattern) in enumerate(itertools.product((False, True), (0, 0xa5))):
    fixture = (True, False, irq_disabled, pattern, 0, True)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('irq_state', index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_QUEUE_UNINIT_IRQ_STATE_NATIVE_SOURCE',
          'cases': len(fixtures) + 4, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['IRQ enable at 0x48009e intercepted; queue disable and IRQ state read executed.',
                     'Synthetic SRAM/MMIO only; physical operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 4)
