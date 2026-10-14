#!/usr/bin/env python3
"""Compare Main 0x53916e queue reset with the locked native body."""
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
QUEUE, OPS, REGS, RET = 0x20006000, 0x20008000, 0x20009000, 0x200ff000

def run(source, magic, busy, initial, pattern, null_queue):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(QUEUE, bytes([pattern]) * 0x80)
    cpu.mem_write(OPS, bytes([pattern]) * 0x20)
    cpu.mem_write(REGS, bytes([pattern]) * 0x20)
    cpu.mem_write(QUEUE, (magic | (0x02000000 if busy else 0)).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 4, initial.to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 9*4, OPS.to_bytes(4, 'little'))
    for i in range(4):
        cpu.mem_write(OPS + i*4, (REGS + i*4).to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, 0 if null_queue else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    def hook(machine, pc, _size, _user):
        if pc == RET: machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_queue_reset_53916e'] if source else 0x53916e
    cpu.emu_start(entry | 1, RET + 2, count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), bytes(cpu.mem_read(QUEUE, 0x80)),
            bytes(cpu.mem_read(OPS, 0x20)), bytes(cpu.mem_read(REGS, 0x20)))

fixtures = list(itertools.product((0x01cdcdcd, 0x01bebebe, 0), (False, True),
                                  (0, 1, 0x12345678, 0xffffffff),
                                  (0, 0x55, 0xa5), (False, True)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        diff = [(field, hex(i), hex(x), hex(y)) for field in range(1,4)
                for i,(x,y) in enumerate(zip(native[field], candidate[field])) if x != y]
        raise AssertionError((index, fixture, native[0], candidate[0], diff[:16]))
report = {'status': 'PASS_MAIN_QUEUE_RESET_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic SRAM register and ops row; concurrent queue use unverified.',
                     'Full Main image and physical hardware unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
