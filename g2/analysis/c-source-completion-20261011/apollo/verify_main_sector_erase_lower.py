#!/usr/bin/env python3
"""Bounded native/source MX25U25643G sector erase control-path oracle."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as reg

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = 0x437fe0
RET = 0x20000000
SP = 0x200ff000
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
stock = STOCK.read_bytes()
assert hashlib.sha256(stock).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    segments = [(part['p_vaddr'], part.data()) for part in elf.iter_segments()
                if part['p_type'] == 'PT_LOAD' and part['p_filesz']]
    source_entry = next(item['st_value'] & ~1 for item in
                        elf.get_section_by_name('.symtab').iter_symbols()
                        if item.name == 'g2_norflash_erase_lower_47075c')

def cstring(cpu, address):
    data = bytearray()
    while len(data) < 256:
        value = cpu.mem_read(address + len(data), 1)[0]
        if value == 0:
            return data.decode()
        data.append(value)
    raise AssertionError('unterminated string')

HELPERS = {
    0x46f65e: 'lock', 0x46f674: 'unlock',
    0x470f68: 'enter', 0x470e90: 'exit',
    0x4703ba: 'wait_idle', 0x470670: 'write_enable',
    0x47021c: 'erase_command', 0x4706e0: 'write_disable',
}

def run(entry, address, handle, flags, failure):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(BASE, stock)
    cpu.mem_map(0x800000, 0x10000)
    for start, data in segments:
        cpu.mem_write(start, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(0x20074544, handle.to_bytes(4, 'little'))
    events = []
    waits = 0
    def hook(machine, pc, insn_size, unused):
        nonlocal waits
        if pc in HELPERS:
            name = HELPERS[pc]
            if name == 'erase_command':
                extra = int.from_bytes(machine.mem_read(machine.reg_read(reg.UC_ARM_REG_SP), 4), 'little')
                events.append((name, *[machine.reg_read(r) for r in
                                      (reg.UC_ARM_REG_R0, reg.UC_ARM_REG_R1,
                                       reg.UC_ARM_REG_R2, reg.UC_ARM_REG_R3)], extra))
            else:
                events.append((name,))
            value = 0
            if name == 'wait_idle':
                value = int(failure == ('wait_before' if waits == 0 else 'wait_after'))
                waits += 1
            elif name == 'write_enable' and failure == name:
                value = 7
            elif name == 'erase_command' and failure == name:
                value = 8
            elif name == 'write_disable' and failure == name:
                value = 9
            machine.reg_write(reg.UC_ARM_REG_R0, value)
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x4733ee:
            fmt = cstring(machine, machine.reg_read(reg.UC_ARM_REG_R0))
            r1 = machine.reg_read(reg.UC_ARM_REG_R1)
            r2 = machine.reg_read(reg.UC_ARM_REG_R2)
            events.append(('diagnostic', fmt, r1, r2 if 'st=%d' in fmt else None))
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43d0ce:
            events.append(('flags',))
            machine.reg_write(reg.UC_ARM_REG_R0, flags)
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43d574:
            stack = machine.reg_read(reg.UC_ARM_REG_SP)
            line = int.from_bytes(machine.mem_read(stack, 4), 'little')
            fmt = int.from_bytes(machine.mem_read(stack + 4, 4), 'little')
            events.append(('extended', machine.reg_read(reg.UC_ARM_REG_R0),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R1)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R2)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R3)),
                           line, cstring(machine, fmt)))
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43ce9e:
            events.append(('simple', machine.reg_read(reg.UC_ARM_REG_R0),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R1)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R2))))
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(reg.UC_ARM_REG_SP, SP)
    cpu.reg_write(reg.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(reg.UC_ARM_REG_R0, address)
    cpu.emu_start(entry | 1, RET + 2, count=2000)
    assert cpu.reg_read(reg.UC_ARM_REG_PC) == RET
    assert cpu.reg_read(reg.UC_ARM_REG_SP) == SP
    return {'result': cpu.reg_read(reg.UC_ARM_REG_R0), 'events': events}

cases = 0
addresses = (0, 1, 0x1000, 0x1fff000, 0x2000000, 0x80000000,
             0xfffff000)
for address, handle, flags, failure in itertools.product(
        addresses, (0, 0x20070000), (0, 1, 2, 3, 4, 7),
        (None, 'wait_before', 'write_enable', 'erase_command',
         'wait_after', 'write_disable')):
    original = run(0x47075c, address, handle, flags, failure)
    source = run(source_entry, address, handle, flags, failure)
    assert original == source, (address, handle, flags, failure, original, source)
    cases += 1
result = {'status': 'PASS_MAIN_SECTOR_ERASE_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': hashlib.sha256(stock).hexdigest(),
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Physical flash helpers, diagnostic formatter and logger are injected equally; only the sector erase control path is compared.',
                     'The selected controller handle is a named unresolved SRAM owner; fixture values test null and nonnull branches.',
                     'No hardware timing or actual flash write/erase is qualified.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], cases)
