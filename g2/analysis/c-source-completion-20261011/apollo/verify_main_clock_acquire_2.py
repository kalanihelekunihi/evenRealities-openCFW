#!/usr/bin/env python3
"""Locked Main/source class 2 acquire orchestration comparison."""
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
TABLE, TIMEOUT, RET = 0x20073324, 0x20009000, 0x200ff000
NATIVE = {0x473940: 'critical', 0x480c56: 'mode_read',
          0x4809c4: 'mode_set', 0x4c3d70: 'cleanup'}
SOURCE = {syms['g2_main_critical_save_473940']: 'critical',
          syms['g2_main_clock_mode_read_480c56']: 'mode_read',
          syms['g2_main_clock_mode_set_4809c4']: 'mode_set',
          syms['g2_main_clock_timeout_cleanup_4c3d70']: 'cleanup'}

def run(source, ready, present, mode, selected, active, seed, mask, second):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(TABLE, bytes(56))
    if present:
        cpu.mem_write(TABLE + 16, (1 << 11).to_bytes(4, 'little'))
    cpu.mem_write(0x200001d0, ready.to_bytes(4, 'little'))
    cpu.mem_write(0x200001cc, bytes([selected]))
    cpu.mem_write(0x20074f56, bytes([active]))
    cpu.mem_write(0x20074260, TIMEOUT.to_bytes(4, 'little'))
    cpu.mem_write(TIMEOUT, seed.to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, 11)
    cpu.reg_write(R.UC_ARM_REG_R1, second)
    cpu.reg_write(R.UC_ARM_REG_R2, 0x87654321)
    cpu.reg_write(R.UC_ARM_REG_R3, 0xabcdef01)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    events = []
    helpers = SOURCE if source else NATIVE
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc in helpers:
            name = helpers[pc]
            if name == 'critical':
                events.append((name,))
                machine.reg_write(R.UC_ARM_REG_R0, mask)
                machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            elif name == 'mode_read':
                events.append((name,))
                machine.mem_write(machine.reg_read(R.UC_ARM_REG_R0), bytes([mode]))
                machine.reg_write(R.UC_ARM_REG_R0, 0)
            elif name == 'mode_set':
                operation = machine.reg_read(R.UC_ARM_REG_R0)
                pointer = machine.reg_read(R.UC_ARM_REG_R1)
                choice = machine.mem_read(pointer, 1)[0] if pointer else None
                events.append((name, operation, choice))
                machine.reg_write(R.UC_ARM_REG_R0, 0)
            else:
                pointer = machine.reg_read(R.UC_ARM_REG_R0)
                events.append((name, int.from_bytes(machine.mem_read(pointer, 4), 'little')))
                if machine.mem_read(0x20074f56, 1)[0]:
                    machine.mem_write(0x20074f56, b'\x00')
                    machine.mem_write(0x20074260, bytes(4))
                machine.reg_write(R.UC_ARM_REG_R0, 0)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_clock_acquire_2_4c3d9e'] if source else 0x4c3d9e
    cpu.emu_start(entry | 1, RET + 2, count=6000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    slot = int.from_bytes(cpu.mem_read(0x20074260, 4), 'little')
    if 0x200fd000 <= slot < 0x200fe000:
        slot_state = ('stack', int.from_bytes(cpu.mem_read(slot, 4), 'little'))
    else:
        slot_state = ('fixed', slot)
    return (cpu.reg_read(R.UC_ARM_REG_R0), cpu.reg_read(R.UC_ARM_REG_R1),
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(TABLE, 56)),
            bytes(cpu.mem_read(0x20074f56, 1)), slot_state)

fixtures = list(itertools.product((0, 1), (False, True), (0, 1, 2),
                                  (0, 1, 2), (0, 1), (0, 7, 150),
                                  (0, 1), (0, 0x12345678)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        raise AssertionError((index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_CLOCK_ACQUIRE_2_ORCHESTRATION_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical save, mode read/set and timeout cleanup intercepted.',
                     'Request bitmap and class 2 state changes executed in synthetic SRAM.',
                     'Physical clock transition and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
