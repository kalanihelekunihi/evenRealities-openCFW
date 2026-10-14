#!/usr/bin/env python3
"""Bounded locked Main/source oracle for NOR page-program control flow."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as R

ROOT = Path(__file__).resolve().parents[4]
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
STOCK_SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob = BLOB.read_bytes()
assert hashlib.sha256(blob).hexdigest() == STOCK_SHA
p = argparse.ArgumentParser()
p.add_argument('--elf', type=Path, required=True)
p.add_argument('--receipt', type=Path, required=True)
a = p.parse_args()
with a.elf.open('rb') as f:
    elf = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    syms = {s.name: s['st_value'] & ~1
            for s in elf.get_section_by_name('.symtab').iter_symbols()}

NATIVE = {0x46f65e: 'lock', 0x46f674: 'unlock', 0x470f68: 'enter',
          0x470e90: 'exit', 0x4703ba: 'wait_before',
          0x470670: 'enable', 0x47021c: 'program',
          0x470368: 'wait_after', 0x4706e0: 'disable',
          0x4733ee: 'diagnostic'}
SOURCE = {syms[name]: event for name, event in (
    ('g2_norflash_lock_46f65e', 'lock'),
    ('g2_norflash_unlock_46f674', 'unlock'),
    ('g2_norflash_enter_470f68', 'enter'),
    ('g2_norflash_exit_470e90', 'exit'),
    ('g2_norflash_wait_idle_4703ba', 'wait_before'),
    ('g2_norflash_write_enable_470670', 'enable'),
    ('g2_norflash_erase_command_47021c', 'program'),
    ('g2_norflash_wait_status_470368', 'wait_after'),
    ('g2_norflash_write_disable_4706e0', 'disable'),
    ('g2_norflash_diagnostic_4733ee', 'diagnostic'))}
CONTROLLER, BUFFER, RET = 0x20074544, 0x20008000, 0x200ff000


def word(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 4), 'little')


def put(cpu, address, value):
    cpu.mem_write(address, int(value).to_bytes(4, 'little'))


def string(cpu, address):
    return bytes(cpu.mem_read(address, 256)).split(b'\0', 1)[0].decode('utf-8')


def run(source, controller, buffer, size, address, fail_stage, fail_page):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for segment_address, data in segments:
        cpu.mem_write(segment_address, data)
    cpu.mem_map(0x20000000, 0x100000)
    put(cpu, CONTROLLER, controller)
    cpu.mem_write(BUFFER, bytes([0xa5]) * 1024)
    cpu.reg_write(R.UC_ARM_REG_R0, address)
    cpu.reg_write(R.UC_ARM_REG_R1, buffer)
    cpu.reg_write(R.UC_ARM_REG_R2, size)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    helpers = SOURCE if source else NATIVE
    events = []
    page = -1

    def hook(machine, pc, _length, _user):
        nonlocal page
        if pc == RET:
            machine.emu_stop()
            return
        if pc not in helpers:
            return
        event = helpers[pc]
        r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                          (R.UC_ARM_REG_R0, R.UC_ARM_REG_R1,
                           R.UC_ARM_REG_R2, R.UC_ARM_REG_R3))
        if event == 'wait_before':
            page += 1
            events.append([event])
        elif event == 'program':
            events.append([event, r0, r1, r2, r3,
                           word(machine, machine.reg_read(R.UC_ARM_REG_SP))])
        elif event == 'wait_after':
            events.append([event, r0])
        elif event == 'diagnostic':
            message = string(machine, r0)
            count = message.count('%')
            events.append([event, message, [r1, r2, r3][:count]])
        else:
            events.append([event])
        result = 7 if event == fail_stage and page == fail_page else 0
        machine.reg_write(R.UC_ARM_REG_R0, result)
        machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((syms['g2_norflash_write_lower_4708a8'] if source else 0x4708a8) | 1,
                  RET + 2, count=8000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'result': cpu.reg_read(R.UC_ARM_REG_R0), 'events': events,
            'buffer': bytes(cpu.mem_read(BUFFER, 1024)).hex(),
            'controller': word(cpu, CONTROLLER)}


fixtures = []
for controller, buffer, size, address in itertools.product(
        (0, 0x20006000), (0, BUFFER), (0, 1, 257),
        (0, 0x01ffffff, 0x02000000, 0xffffffff)):
    fixtures.append((controller, buffer, size, address, None, 0))
for address, size, fail_stage, fail_page in itertools.product(
        (0, 1, 0xff, 0x100, 0x1ff), (1, 2, 255, 256, 257, 512),
        (None, 'wait_before', 'enable', 'program', 'wait_after', 'disable'),
        (0, 1)):
    fixtures.append((0x20006000, BUFFER, size, address, fail_stage, fail_page))

for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    assert native == candidate, (index, fixture, native, candidate)
report = {'status': 'PASS_MAIN_NOR_WRITE_LOWER_BOUNDED_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Lock, mode entry/exit, waits, write latch, page command and diagnostics are intercepted.',
                     'Synthetic page boundaries and helper statuses prove control flow, not physical NOR programming.',
                     'No complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
