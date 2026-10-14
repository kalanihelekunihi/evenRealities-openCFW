#!/usr/bin/env python3
"""Locked Main/source class 2 release and final-request shutdown comparison."""
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
TABLE, MMIO, RET = 0x20073324, 0x40020000, 0x200ff000

def run(source, id, requested, other, mask, high, pattern, mux, div):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x2000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x2000)
    cpu.mem_write(0x200001e0, mux.to_bytes(4, 'little'))
    cpu.mem_write(0x200001e4, div.to_bytes(4, 'little'))
    cpu.mem_write(0x20074f56, b'\x01')
    cpu.mem_write(0x20074260, (0x12345678).to_bytes(4, 'little'))
    cpu.mem_write(TABLE, bytes(56))
    if requested:
        address = TABLE + 16 + (id >> 5) * 4
        cpu.mem_write(address, (1 << (id & 31)).to_bytes(4, 'little'))
    if other:
        other_id = (id + 1) % 57
        address = TABLE + 16 + (other_id >> 5) * 4
        old = int.from_bytes(cpu.mem_read(address, 4), 'little')
        cpu.mem_write(address, (old | (1 << (other_id & 31))).to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, id)
    cpu.reg_write(R.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(R.UC_ARM_REG_R2, high)
    cpu.reg_write(R.UC_ARM_REG_R3, 0x87654321)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    events = []
    critical = syms['g2_main_critical_save_473940'] if source else 0x473940
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == critical:
            events.append('critical')
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_clock_release_2_4c3e9a'] if source else 0x4c3e9a
    cpu.emu_start(entry | 1, RET + 2, count=6000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), cpu.reg_read(R.UC_ARM_REG_R1),
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(TABLE, 56)), bytes(cpu.mem_read(MMIO, 0x2000)),
            bytes(cpu.mem_read(0x20074f56, 1)),
            bytes(cpu.mem_read(0x20074260, 4)))

fixtures = list(itertools.product((0, 1, 15, 31, 32, 54, 56),
                                  (False, True), (False, True), (0, 1),
                                  (0, 0x12345678), (0, 0xa5),
                                  (0, 0x12345678), (0, 0xfedcba98)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        differences = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[5], candidate[5])) if x != y]
        raise AssertionError((index, fixture, native[:5], candidate[:5], differences[:12], native[6:], candidate[6:]))
report = {'status': 'PASS_MAIN_CLOCK_RELEASE_2_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical-save helper intercepted; native mode-4 shutdown executed.',
                     'Synthetic SRAM/MMIO only; physical clock behavior and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
