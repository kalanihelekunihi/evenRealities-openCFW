#!/usr/bin/env python3
"""Locked Main/source queue init and IRQ reset comparison."""
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
STATE, OUTPUT, MMIO, RET = 0x200740f4, 0x20009000, 0x40020000, 0x200ff000

def run(source, direct, instance, present, busy, pattern, revision, mask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x2000)
    cpu.mem_write(0x4002000c, revision.to_bytes(4, 'little'))
    cpu.mem_write(STATE, ((0xa4000000 if pattern else 0) |
                          (0x01000000 if busy else 0) |
                          (0x12345 if pattern else 0)).to_bytes(4, 'little'))
    cpu.mem_write(STATE + 4, (0x12345678).to_bytes(4, 'little'))
    cpu.mem_write(OUTPUT, (0xa5a5a5a5).to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, instance)
    cpu.reg_write(R.UC_ARM_REG_R1, OUTPUT if present else 0)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    critical = syms['g2_main_critical_save_473940'] if source else 0x473940
    delay = syms['audio_delay_us_selected'] if source else 0x4807a0
    events = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == critical:
            events.append(('critical',))
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
        elif pc == delay:
            events.append(('delay', machine.reg_read(R.UC_ARM_REG_R0)))
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_irq_disable_480058'] if direct else
             syms['g2_main_queue_init_5398e0']) if source else (0x480058 if direct else 0x5398e0)
    cpu.emu_start(entry | 1, RET + 2, count=6000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            cpu.reg_read(R.UC_ARM_REG_R1) if direct else None,
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(STATE, 8)), bytes(cpu.mem_read(OUTPUT, 4)),
            bytes(cpu.mem_read(MMIO, 0x2000)))

fixtures = list(itertools.product((0, 1), (False, True), (False, True),
                                  (0, 0xa5), (0x20, 0x22, 0xff), (0, 1)))
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture)
    candidate = run(True, False, *fixture)
    if native != candidate:
        differences = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[6], candidate[6])) if x != y]
        raise AssertionError(('init', index, fixture, native[:6], candidate[:6], differences[:12]))
for index, (pattern, revision, mask) in enumerate(itertools.product((0, 0xa5),
                                                                     (0x20, 0x22, 0xff), (0, 1))):
    fixture = (0, True, False, pattern, revision, mask)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('irq_reset', index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_QUEUE_INIT_IRQ_RESET_NATIVE_SOURCE',
          'cases': len(fixtures) + 12, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical save and microsecond delays intercepted; queue and IRQ MMIO changes executed.',
                     'Synthetic SRAM/MMIO only; physical queue operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 12)
