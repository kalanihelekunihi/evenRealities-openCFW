#!/usr/bin/env python3
"""Locked Main/source MSPI transfer selector 29 comparison."""
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
HANDLE, CONFIG, QUEUE, MMIO, RET = 0x20006000, 0x20008000, 0x20009000, 0x40060000, 0x200ff000
NATIVE = {0x4bfd6e: 'terminate', 0x53916e: 'reset'}
SOURCE = {syms['g2_main_mspi_queue_terminate_4bfd6e']: 'terminate',
          syms['g2_main_queue_reset_53916e']: 'reset'}

def run(source, module, selector, valid, enabled, present, choice, ready,
        mode, active, terminate_result, reset_result):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x4000)
    cpu.mem_write(MMIO, bytes([0xa5]) * 0x4000)
    cpu.mem_write(HANDLE, bytes([0xa5]) * 0x900)
    cpu.mem_write(HANDLE, (0x01bebebe if valid else 0).to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 4, module.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 8, bytes([enabled]))
    cpu.mem_write(HANDLE + 0x18, ready.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 0x20, active.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 0x828, QUEUE.to_bytes(4, 'little'))
    cpu.mem_write(HANDLE + 0x82c, bytes([mode]))
    cpu.mem_write(CONFIG, bytes([choice]) * 16)
    cpu.reg_write(R.UC_ARM_REG_R0, HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1, selector)
    cpu.reg_write(R.UC_ARM_REG_R2, CONFIG if present else 0)
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
                              terminate_result if event == 'terminate' else reset_result)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_mspi_transfer_queue_mode_candidate'] if source else 0x4c0f78
    cpu.emu_start(entry | 1, RET + 2, count=10000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), events,
            bytes(cpu.mem_read(HANDLE, 0x900)), bytes(cpu.mem_read(MMIO, 0x4000)))

fixtures = list(itertools.product((0, 2), (29, 0x11d), (False, True), (0, 1),
                                  (False, True), (0, 1), (0, 1), (0, 1, 2, 3),
                                  (0, 1), (0, 4), (0, 7)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        handle_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[2], candidate[2])) if x != y]
        mmio_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[3], candidate[3])) if x != y]
        raise AssertionError((index, fixture, native[:2], candidate[:2], handle_diff[:12], mmio_diff[:12]))
report = {'status': 'PASS_MAIN_MSPI_TRANSFER_SELECTOR29_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Queue termination and reset providers intercepted; independently source-checked in rounds 514 and 519.',
                     'Only selector 29 represented; full dispatcher remains unresolved.',
                     'Synthetic SRAM/MMIO only; physical operation unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
