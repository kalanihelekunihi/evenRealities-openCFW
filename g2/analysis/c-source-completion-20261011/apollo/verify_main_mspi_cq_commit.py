#!/usr/bin/env python3
"""Compare Main CQ commit and rollback bodies with locked native code."""
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
QUEUE, OPS, SLOT, REG, RET = 0x20006000, 0x20008000, 0x20009000, 0x2000a000, 0x200ff000
ENTRIES = {'commit': (0x538fb4, 'g2_main_cq_commit_538fb4'),
           'marker': (0x5391d6, 'g2_main_cq_commit_marker_5391d6'),
           'rollback': (0x538f82, 'g2_main_cq_rollback_538f82')}

def run(source, kind, valid, reserved, marker, index, pattern, barrier):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    for address, size in ((QUEUE, 0x80), (OPS, 0x20), (SLOT, 0x80), (REG, 0x20)):
        cpu.mem_write(address, bytes([pattern]) * size)
    cpu.mem_write(QUEUE, (0x01cdcdcd if valid else 0).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 4, (SLOT + 0x40).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 8, (0x20080000 if barrier else 0x20010000).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 16, SLOT.to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 20, (SLOT + (4 if reserved else 0)).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 32, index.to_bytes(4, 'little'))
    cpu.mem_write(QUEUE + 36, OPS.to_bytes(4, 'little'))
    for offset, value in ((4, 0x12340000), (8, 0x56780000), (12, REG)):
        cpu.mem_write(OPS + offset, value.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, QUEUE)
    cpu.reg_write(R.UC_ARM_REG_R1, marker)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    def hook(machine, pc, _size, _user):
        if pc == RET: machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, hook)
    native_entry, source_name = ENTRIES[kind]
    cpu.emu_start((syms[source_name] if source else native_entry) | 1, RET + 2, count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            bytes(cpu.mem_read(QUEUE, 0x80)), bytes(cpu.mem_read(SLOT, 0x80)),
            bytes(cpu.mem_read(REG, 0x20)))

fixtures = list(itertools.product(ENTRIES, (False, True), (False, True),
                                  (0, 1, 0x100), (0, 1, 0x123),
                                  (0, 0xa5), (False, True)))
for case, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        diff = [(field, hex(i), hex(x), hex(y)) for field in range(1,4)
                for i,(x,y) in enumerate(zip(native[field],candidate[field])) if x != y]
        raise AssertionError((case, fixture, native[0], candidate[0], diff[:16]))
report = {'status': 'PASS_MAIN_MSPI_CQ_COMMIT_ROLLBACK_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Synthetic queue, descriptor SRAM and index register; concurrency and physical hardware unverified.',
                     'Queue reservation provider and full transfer dispatcher remain unresolved.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
