#!/usr/bin/env python3
"""Locked Main/source queue configuration and pin-mode comparison."""
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
QUEUE, CONFIG, RET = 0x20008000, 0x20009000, 0x200ff000

def run(source, direct, valid, active, mode, count, length, index, flag, pattern, mask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(0x437fe0, blob)
    cpu.mem_map(0x800000, 0x10000)
    for address, body in segments:
        cpu.mem_write(address, body)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x40008000, 0x1000)
    cpu.mem_map(0x40020000, 0x2000)
    cpu.mem_write(0x40008000, bytes([pattern]) * 0x1000)
    cpu.mem_write(0x40020000, bytes([pattern]) * 0x2000)
    cpu.mem_write(QUEUE, ((0x01504c30 if valid else 0) |
                          (0x02000000 if active else 0)).to_bytes(4, 'little'))
    data = bytearray([0x5a] * 16)
    data[0] = flag
    data[1] = 1
    data[2] = mode
    data[3] = length
    data[4] = index[0]
    data[5] = index[1]
    data[6:8] = count.to_bytes(2, 'little')
    cpu.mem_write(CONFIG, bytes(data))
    cpu.reg_write(R.UC_ARM_REG_R0, flag if direct else QUEUE)
    cpu.reg_write(R.UC_ARM_REG_R1, CONFIG)
    cpu.reg_write(R.UC_ARM_REG_R3, 0x12345678)
    cpu.reg_write(R.UC_ARM_REG_SP, 0x200fe000)
    cpu.reg_write(R.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(R.UC_ARM_REG_PRIMASK, mask)
    critical = syms['g2_main_critical_save_473940'] if source else 0x473940
    events = []
    def hook(machine, pc, _size, _user):
        if pc == RET:
            machine.emu_stop()
        elif pc == critical:
            events.append('critical')
            machine.reg_write(R.UC_ARM_REG_R0, mask)
            machine.reg_write(R.UC_ARM_REG_PRIMASK, 1)
            machine.reg_write(R.UC_ARM_REG_PC, machine.reg_read(R.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = (syms['g2_main_queue_pin_mode_44b0b6'] if direct else
             syms['g2_main_queue_config_539a40']) if source else (0x44b0b6 if direct else 0x539a40)
    cpu.emu_start(entry | 1, RET + 2, count=6000)
    assert cpu.reg_read(R.UC_ARM_REG_PC) == RET
    return (cpu.reg_read(R.UC_ARM_REG_R0),
            cpu.reg_read(R.UC_ARM_REG_R1) if direct else None,
            cpu.reg_read(R.UC_ARM_REG_PRIMASK), events,
            bytes(cpu.mem_read(QUEUE, 4)),
            bytes(cpu.mem_read(0x40008000, 0x1000)),
            bytes(cpu.mem_read(0x40020000, 0x2000)))

fixtures = [(True, False, mode, count, length, index, flag, pattern, 0)
            for mode, count, length, index, flag, pattern in
            itertools.product((0, 1, 2), (0, 4, 9, 10, 96, 960, 961, 65535),
                              (0, 63, 64), ((0, 0), (7, 7), (0, 1), (8, 0)),
                              (0, 1, 2), (0, 0xa5))]
fixtures += [(valid, active, 1, 10, 8, (7, 7), 1, pattern, mask)
             for valid, active, pattern, mask in
             itertools.product((False, True), (False, True), (0, 0xa5), (0, 1))]
for index, fixture in enumerate(fixtures):
    native = run(False, False, *fixture)
    candidate = run(True, False, *fixture)
    if native != candidate:
        pin_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[5], candidate[5])) if x != y]
        queue_diff = [(hex(i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(native[6], candidate[6])) if x != y]
        raise AssertionError(('config', index, fixture, native[:5], candidate[:5], pin_diff[:8], queue_diff[:8]))
for index, (flag, pattern, mask) in enumerate(itertools.product((0, 1, 2), (0, 0xa5), (0, 1))):
    fixture = (True, False, 1, 10, 0, (0, 0), flag, pattern, mask)
    native = run(False, True, *fixture)
    candidate = run(True, True, *fixture)
    if native != candidate:
        raise AssertionError(('pin', index, fixture, native[:5], candidate[:5]))
report = {'status': 'PASS_MAIN_QUEUE_CONFIG_PIN_MODE_NATIVE_SOURCE',
          'cases': len(fixtures) + 12, 'stock_sha256': SHA,
          'source_elf_sha256': hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          'limits': ['Critical-save helper intercepted; queue and pin MMIO writes executed.',
                     'Synthetic MMIO/SRAM only; physical queue operation and complete Main image unverified.']}
a.receipt.parent.mkdir(parents=True, exist_ok=True)
a.receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], len(fixtures) + 12)
