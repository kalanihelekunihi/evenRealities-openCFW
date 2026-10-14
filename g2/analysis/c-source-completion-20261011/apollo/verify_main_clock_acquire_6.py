#!/usr/bin/env python3
"""Locked Main/source class 6 acquire orchestration comparison."""
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
TABLE, QUEUE, RET = 0x20073324, 0x20008000, 0x200ff000
HELPERS = {
    'critical': (0x473940, 'g2_main_critical_save_473940'),
    'count': (0x4c37ca, 'g2_main_clock_request_count_4c37ca'),
    'acquire2': (0x4c3d9e, 'g2_main_clock_acquire_2_4c3d9e'),
    'acquire3': (0x4c3cd4, 'g2_main_clock_acquire_3_4c3cd4'),
    'release2': (0x4c3e9a, 'g2_main_clock_release_2_4c3e9a'),
    'release3': (0x4c3d28, 'g2_main_clock_release_3_4c3d28'),
    'init': (0x5398e0, 'g2_main_queue_init_5398e0'),
    'config': (0x539a40, 'g2_main_queue_config_539a40'),
    'enable': (0x539994, 'g2_main_queue_enable_539994'),
    'uninit': (0x539944, 'g2_main_queue_uninit_539944'),
    'start': (0x539b56, 'g2_main_queue_start_539b56'),
}
NATIVE = {address: name for name, (address, _) in HELPERS.items()}
SOURCE = {syms[symbol]: name for name, (_, symbol) in HELPERS.items()}

def run(source, present, other, clock_flag, mode, queue_present, active,
        failure, mask, high):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(TABLE, bytes(56))
    if present:
        cpu.mem_write(TABLE + 48, (1 << 11).to_bytes(4, 'little'))
    if other:
        old = int.from_bytes(cpu.mem_read(TABLE + 48, 4), 'little')
        cpu.mem_write(TABLE + 48, (old | 1).to_bytes(4, 'little'))
    cpu.mem_write(0x20074f55, bytes([clock_flag]))
    cpu.mem_write(0x20073f48, bytes([mode]))
    cpu.mem_write(0x20074f5b, bytes([active]))
    cpu.mem_write(0x2007425c, (QUEUE if queue_present else 0).to_bytes(4, 'little'))
    cpu.mem_write(QUEUE, (0x01504c30).to_bytes(4, 'little'))
    cpu.reg_write(R.UC_ARM_REG_R0, 11)
    cpu.reg_write(R.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(R.UC_ARM_REG_R2, high)
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
            events.append((name, None if name == 'critical' else machine.reg_read(R.UC_ARM_REG_R0),
                           machine.reg_read(R.UC_ARM_REG_R1) if name in ('init', 'config') else None))
            if name == 'critical':
                machine.reg_write(R.UC_ARM_REG_R0, mask)
                machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            elif name == 'count':
                machine.reg_write(R.UC_ARM_REG_R0, int(present) + int(other))
            else:
                result = 5 if failure == name else 0
                if name == 'init' and result == 0:
                    machine.mem_write(machine.reg_read(R.UC_ARM_REG_R1), QUEUE.to_bytes(4, 'little'))
                machine.reg_write(R.UC_ARM_REG_R0, result)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = syms['g2_main_clock_acquire_6_4c427e'] if source else 0x4c427e
    cpu.emu_start(entry | 1, RET + 2, count=8000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0), cpu.reg_read(R.UC_ARM_REG_R1),
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(TABLE, 56)),
            bytes(cpu.mem_read(0x20074f55, 1)),
            bytes(cpu.mem_read(0x20074f5b, 1)),
            bytes(cpu.mem_read(0x2007425c, 4)))

fixtures = list(itertools.product((False, True), (False, True), (0, 1),
                                  (0, 1), (False, True), (0, 1),
                                  ('none', 'acquire2', 'acquire3', 'init',
                                   'config', 'enable', 'start'), (0, 1),
                                  (0, 0x12345678)))
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        raise AssertionError((index, fixture, native, candidate))
report = {'status': 'PASS_MAIN_CLOCK_ACQUIRE_6_ORCHESTRATION_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Clock count, critical save and downstream clock/queue lifecycle calls intercepted.',
                     'Request bitmap and class 6 state changes executed in synthetic SRAM.',
                     'Physical queue/clock operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
