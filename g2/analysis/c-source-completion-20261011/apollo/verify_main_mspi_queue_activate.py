#!/usr/bin/env python3
"""Compare Main queue activate 0x4bfe60 with its C candidate."""
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
HANDLE, MMIO, RET = 0x20006000, 0x40060000, 0x200ff000
NATIVE = {0x473940: 'critical', 0x4bfd6e: 'terminate', 0x4bfdf4: 'descriptor'}
SOURCE = {syms['g2_main_critical_save_473940']: 'critical',
          syms['g2_main_mspi_queue_terminate_4bfd6e']: 'terminate',
          syms['g2_main_mspi_queue_descriptor_4bfdf4']: 'descriptor'}

def run(source, module, previous, increment, terminate, descriptor, saved, pattern):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x4000)
    cpu.mem_write(MMIO, bytes([pattern]) * 0x4000)
    cpu.mem_write(HANDLE, bytes([0xa5]) * 0x900)
    cpu.mem_write(HANDLE + 4, module.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 0x840, previous.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1, increment)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    helpers = SOURCE if source else NATIVE
    events = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc in helpers:
            event = helpers[pc]
            events.append((event, machine.reg_read(R.UC_ARM_REG_R0)))
            machine.reg_write(R.UC_ARM_REG_R0,
                              saved if event == 'critical' else
                              terminate if event == 'terminate' else descriptor)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_mspi_queue_activate_4bfe60'] if source else 0x4bfe60
    cpu.emu_start(entry | 1, RET + 2, count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), cpu.reg_read(R.UC_ARM_REG_R1), events,
            bytes(cpu.mem_read(HANDLE, 0x900)), bytes(cpu.mem_read(MMIO, 0x4000)))

fixtures = list(itertools.product(range(4), (0, 1, 5), (0, 1, 0xffffffff),
                                  (0, 4), (0, 5), (0, 1), (0, 0xa5)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        handle_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[3], candidate[3])) if x != y]
        mmio_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[4], candidate[4])) if x != y]
        raise AssertionError((index, fixture, native[:3], candidate[:3], handle_diff[:12], mmio_diff[:12]))
report = {'status': 'PASS_MAIN_MSPI_QUEUE_ACTIVATE_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical save, queue terminate and descriptor load providers intercepted; latter two independently checked in rounds 514 and 516.',
                     'Synthetic SRAM/MMIO only; physical queue operation unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
