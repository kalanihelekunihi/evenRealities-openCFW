#!/usr/bin/env python3
"""Locked native/source MSPI configuration comparison with intercepted lowers."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
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
    syms = {s.name: s['st_value'] & ~1 for s in
            elf.get_section_by_name('.symtab').iter_symbols()}
NATIVE = {0x4c0758: 'route', 0x4c4530: 'release',
          0x4c44bc: 'acquire', 0x4bfed6: 'aux', 0x4c07d0: 'finish'}
SOURCE = {syms[name]: event for name, event in (
    ('g2_main_mspi_clock_route_4c0758', 'route'),
    ('g2_main_mspi_clock_release_4c4530', 'release'),
    ('g2_main_mspi_clock_acquire_4c44bc', 'acquire'),
    ('g2_main_mspi_configure_aux_4bfed6', 'aux'),
    ('g2_main_mspi_configure_finish_4c07d0', 'finish'))}
HANDLE, CONFIG, MMIO, RET = 0x20006000, 0x20008000, 0x40060000, 0x200ff000


def put(cpu, addr, val):
    cpu.mem_write(addr, int(val).to_bytes(4, 'little'))


def run(source, module, enabled, serial, parallel, clock_old, clock_fail,
        queue, mode, settings):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(MMIO, 0x4000)
    cpu.mem_write(HANDLE, bytes([0xa5]) * 0x900)
    cpu.mem_write(CONFIG, bytes([0xcc]) * 0x20)
    cpu.mem_write(MMIO, bytes([0xa5]) * 0x4000)
    put(cpu, HANDLE, 0x01bebebe)
    put(cpu, HANDLE + 4, module)
    put(cpu, HANDLE + 24, queue)
    cpu.mem_write(HANDLE + 8, bytes([enabled]))
    cpu.mem_write(HANDLE + 13, bytes([0x5a]))
    cpu.mem_write(HANDLE + 0x8c9, bytes([clock_old]))
    cfg = bytearray([0] * 0x20)
    cfg[0] = settings & 0x3f
    cfg[1] = (settings >> 8) & 0x3
    cfg[2] = (settings >> 10) & 1
    cfg[4:8] = bytes.fromhex('12345678')
    cfg[8] = (settings >> 16) & 0xff
    cfg[9] = (settings >> 24) & 0xff
    cfg[10] = 2
    cfg[11] = serial
    cfg[12] = 3
    cfg[13:16] = bytes([1, 0, 1])
    cfg[16] = 1
    cfg[17] = parallel
    cfg[18] = 2
    cfg[20:23] = bytes.fromhex('ab4c0d')
    cpu.mem_write(CONFIG, bytes(cfg))
    cpu.reg_write(R.UC_ARM_REG_R0, HANDLE)
    cpu.reg_write(R.UC_ARM_REG_R1, CONFIG)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    events = []
    helpers = SOURCE if source else NATIVE

    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
            return
        event = helpers.get(pc)
        if event is None:
            return
        args = [machine.reg_read(r) for r in (R.UC_ARM_REG_R0,
                R.UC_ARM_REG_R1, R.UC_ARM_REG_R2, R.UC_ARM_REG_R3)]
        events.append([event, args[:4 if event == 'route' else
                                    2 if event in ('release', 'acquire') else 1]])
        machine.reg_write(R.UC_ARM_REG_R0,
                          9 if event == clock_fail else 0)
        machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start((syms['g2_norflash_configure_mspi_4c099c']
                   if source else 0x4c099c) | 1, RET + 2, count=12000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return {'r0': cpu.reg_read(R.UC_ARM_REG_R0), 'events': events,
            'handle': bytes(cpu.mem_read(HANDLE, 0x900)).hex(),
            'mmio': bytes(cpu.mem_read(MMIO, 0x4000)).hex()}


fixtures = list(itertools.product((0, 1, 2, 3), (0, 1),
                  (0, 1, 2, 3, 4, 9, 17, 18, 19, 20, 21, 22, 23, 24),
                  (0, 1), (4, 5), (None, 'release', 'acquire'),
                  (0, 0x20008000), (0,), (0x12030405,)))
# Sample the broad cross product deterministically, then add queue, mode,
# high-frequency and invalid configurations as dedicated edge cases.
fixtures = fixtures[::37][:240]
fixtures += [(m, 1, s, p, c, f, q, 0, x) for m, s, p, c, f, q, x in
             itertools.product((0, 1), (1, 3, 17, 18, 20, 21, 22, 23),
                               (0, 1), (4, 5), (None, 'release'),
                               (0, 0x20008000), (0x12030405,))]
for index, fixture in enumerate(fixtures):
    native = run(False, *fixture)
    candidate = run(True, *fixture)
    if native != candidate:
        print('MISMATCH', index, fixture)
        for key in native:
            if native[key] != candidate[key]:
                if key in ('handle', 'mmio'):
                    left, right = bytes.fromhex(native[key]), bytes.fromhex(candidate[key])
                    print(key, [(hex(i), hex(x), hex(y)) for i, (x, y) in
                                enumerate(zip(left, right)) if x != y][:32])
                else:
                    print(key, native[key], candidate[key])
        raise AssertionError('native/source mismatch')
report = {'status': 'PASS_MAIN_MSPI_CONFIGURE_BOUNDED_NATIVE_SOURCE',
          'cases': len(fixtures), 'stock_sha256': STOCK_SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Clock route, release/acquire, auxiliary and finish helpers are intercepted.',
                     'Synthetic MMIO and SRAM prove bounded state effects, not physical MSPI configuration.',
                     'No complete Main image is verified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures))
