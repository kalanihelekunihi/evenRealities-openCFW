#!/usr/bin/env python3
"""Locked Main/source clock mode operations 0..6 comparison."""
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
CONFIG, MMIO, RET = 0x20009000, 0x40020000, 0x200ff000
NATIVE_HELPERS = {0x4c44bc: 'acquire', 0x4c4530: 'release', 0x4807a0: 'delay'}
SOURCE_HELPERS = {syms['g2_main_mspi_clock_acquire_4c44bc']: 'acquire',
                  syms['g2_main_mspi_clock_release_4c4530']: 'release',
                  syms['audio_delay_us_selected']: 'delay'}

def run(source, operation, present, value, pattern, mux, divisor, error, high):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x2000)
    cpu.mem_write(CONFIG, value.to_bytes(4, 'little'))
    cpu.mem_write(0x200001e0, mux.to_bytes(4, 'little'))
    cpu.mem_write(0x200001e4, divisor.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, operation)
    cpu.reg_write(R.UC_ARM_REG_R1, CONFIG if present else 0)
    cpu.reg_write(R.UC_ARM_REG_R2, 0x87654321)
    cpu.reg_write(R.UC_ARM_REG_R3, high)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    events = []
    helpers = SOURCE_HELPERS if source else NATIVE_HELPERS
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc in helpers:
            event = helpers[pc]
            events.append((event, machine.reg_read(R.UC_ARM_REG_R0),
                           machine.reg_read(R.UC_ARM_REG_R1) if event != 'delay' else None))
            machine.reg_write(R.UC_ARM_REG_R0, error if event != 'delay' else 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_clock_mode_set_4809c4'] if source else 0x4809c4
    cpu.emu_start(entry | 1, RET + 2, count=6000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), cpu.reg_read(R.UC_ARM_REG_R1),
            events, bytes(cpu.mem_read(MMIO, 0x2000)),
            bytes(cpu.mem_read(CONFIG, 4)))

fixtures = list(itertools.product(range(8), (False, True),
                                  (0, 1, 2, 3, 7, 8, 0xffffffff),
                                  (0, 0xa5), (0, 0x12345678),
                                  (0, 0xfedcba98), (0, 5),
                                  (0, 0x23456789)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        differences = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[3], candidate[3])) if x != y]
        raise AssertionError((index, fixture, native[:3], candidate[:3], differences[:12]))
report = {'status': 'PASS_MAIN_CLOCK_MODE_SET_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['MSPI clock acquire/release and microsecond delay intercepted.',
                     'Synthetic SRAM/MMIO only; physical clock transitions and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
