#!/usr/bin/env python3
"""Compare Main MSPI transfer selectors 28, 31, 32 with the locked binary."""
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
                  if s.name == 'g2_main_mspi_transfer_queue_state_candidate')

HANDLE, CONFIG, MMIO, RET = 0x20006000, 0x20008000, 0x40060000, 0x200ff000

def run(is_source, module, valid, enabled, selector, present, data, pattern, busy):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for addr, body in segments:
        cpu.mem_write(addr, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x4000)
    cpu.mem_write(HANDLE, bytes([0xa5]) * 0x900)
    cpu.mem_write(HANDLE, (0x01bebebe if valid else 0).to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 4, module.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 8, bytes([enabled]))
    cpu.mem_write(HANDLE + 0x854, busy.to_bytes(4, 'little'))
    cpu.mem_write(CONFIG, data)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x4000)
    for reg, value in zip((R.UC_ARM_REG_R0, R.UC_ARM_REG_R1, R.UC_ARM_REG_R2),
                          (HANDLE, selector, CONFIG if present else 0)):
        cpu.reg_write(reg, value)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    def stop(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, stop)
    cpu.emu_start((source if is_source else 0x4c0f78) | 1, RET + 2, count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), bytes(cpu.mem_read(MMIO, 0x4000)),
            bytes(cpu.mem_read(HANDLE, 0x900)), bytes(cpu.mem_read(CONFIG, len(data))))

patterns = (bytes(32), bytes([0xff]) * 32, bytes([0x55, 0xaa]) * 16,
            bytes(range(32)))
addresses = {
    0: (0x5fffffff, 0x60000000, 0x6fffffff, 0x70000000),
    1: (0x7fffffff, 0x80000000, 0x83ffffff, 0x84000000),
    2: (0x83ffffff, 0x84000000, 0x87ffffff, 0x88000000),
    3: (0x87ffffff, 0x88000000, 0x8fffffff, 0x90000000),
}
fixtures = []
for module, selector, raw, pattern in itertools.product(range(4), (28, 31, 32), patterns, (0, 0xa5)):
    fixtures.append((module, True, 1, selector, True, raw, pattern, 0))
for module, selector, present, valid, enabled in itertools.product(range(4), (28, 31, 32),
                                                                  (False, True), (False, True), (0, 1)):
    fixtures.append((module, valid, enabled, selector, present, patterns[3], 0, 0))
for module, raw, pattern in itertools.product(range(4), patterns, (0, 0xa5)):
    fixtures.append((module, True, 1, 31, True, raw, pattern, 1))
for index, fixture in enumerate(fixtures):
    native, candidate = run(False, *fixture), run(True, *fixture)
    if native != candidate:
        differences = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[1], candidate[1])) if x != y]
        config_diff = [(i, x, y) for i, (x, y) in enumerate(zip(native[3], candidate[3])) if x != y]
        raise AssertionError((index, fixture[:5], native[0], candidate[0], differences[:12], config_diff[:12]))
report = {'status': 'PASS_MAIN_MSPI_TRANSFER_QUEUE_STATE_SELECTORS_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Only selectors 28, 31, 32 represented; full dispatcher remains unresolved.',
                     'Synthetic SRAM/MMIO only; physical hardware operation unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
