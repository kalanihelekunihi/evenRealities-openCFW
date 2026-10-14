#!/usr/bin/env python3
"""Locked Main/source queue start and register polling comparison."""
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
QUEUE, MMIO, RET = 0x20008000, 0x40020000, 0x200ff000

def run(source, direct, valid, enabled, factor, timing, ready, flip, iterations, equal):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(QUEUE, (0x01504c30 if valid else 0).to_bytes(4, 'little'))
    cpu.mem_write(0x400204d8, ((0x20000000 if enabled else 0) |
                                   (0x200 if factor else 0)).to_bytes(4, 'little'))
    cpu.mem_write(0x400204e0, timing.to_bytes(4, 'little'))
    cpu.mem_write(0x400204e4, ready.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, iterations if direct else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_R1, 0x400204e4 if direct else 0)
    cpu.reg_write(R.UC_ARM_REG_R2, 1)
    cpu.reg_write(R.UC_ARM_REG_R3, 1)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.mem_write(0x200fe000, equal.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    delay = syms['audio_delay_us_selected'] if source else 0x4807a0
    calls = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == delay:
            calls.append(machine.reg_read(R.UC_ARM_REG_R0))
            if len(calls) == flip:
                machine.mem_write(0x400204e4, (1 - ready).to_bytes(4, 'little'))
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_wait_bits_480826'] if direct else
             syms['g2_main_queue_start_539b56']) if source else (0x480826 if direct else 0x539b56)
    cpu.emu_start(entry | 1, RET + 2, count=30000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), calls,
            bytes(cpu.mem_read(QUEUE, 4)),
            bytes(cpu.mem_read(MMIO, 0x2000)))

fixtures = list(itertools.product((False, True), (False, True), (0, 1),
                                  (0, 1, 2, 3), (0, 1), (1, 2, 999)))
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture, 0, 1)
    candidate = run(True, False, *fixture, 0, 1)
    if native != candidate:
        raise AssertionError(('start', index, fixture, native[:3], candidate[:3]))
for index, (iterations, ready, flip, equal) in enumerate(itertools.product(
        (0, 1, 2, 5), (0, 1), (1, 2, 999), (0, 1))):
    fixture = (True, True, 0, 0, ready, flip, iterations, equal)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('poll', index, fixture, native[:3], candidate[:3]))
report = {'status': 'PASS_MAIN_QUEUE_START_POLL_NATIVE_SOURCE',
          'cases': len(fixtures) + 48, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Microsecond delay intercepted, with deterministic readiness changes after selected calls.',
                     'Synthetic MMIO only; physical queue timing and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 48)
