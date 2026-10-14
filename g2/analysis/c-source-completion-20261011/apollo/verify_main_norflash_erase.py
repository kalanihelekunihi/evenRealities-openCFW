#!/usr/bin/env python3
"""Bounded stock/source FAL erase adapter oracle with shared lower hooks."""
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
    entry_source = next(item['st_value'] & ~1 for item in
                        elf.get_section_by_name('.symtab').iter_symbols()
                        if item.name == 'g2_norflash_erase_540f84')

def cstring(cpu, address):
    data = bytearray()
    while len(data) < 256:
        value = cpu.mem_read(address + len(data), 1)[0]
        if value == 0:
            return data.decode()
        data.append(value)
    raise AssertionError('unterminated string')

def run(entry, offset, size, flags, fail_at):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(BASE, stock)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    events = []
    erases = 0
    def hook(machine, pc, insn_size, unused):
        nonlocal erases
        if pc == 0x47075c:
            address = machine.reg_read(reg.UC_ARM_REG_R0)
            events.append(('erase', address))
            machine.reg_write(reg.UC_ARM_REG_R0, int(erases == fail_at))
            erases += 1
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43d0ce:
            events.append(('flags',))
            machine.reg_write(reg.UC_ARM_REG_R0, flags)
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43d574:
            stack = machine.reg_read(reg.UC_ARM_REG_SP)
            line = int.from_bytes(machine.mem_read(stack, 4), 'little')
            fmt = int.from_bytes(machine.mem_read(stack + 4, 4), 'little')
            argument = int.from_bytes(machine.mem_read(stack + 8, 4), 'little')
            events.append(('extended', machine.reg_read(reg.UC_ARM_REG_R0),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R1)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R2)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R3)), line,
                           cstring(machine, fmt), argument))
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == 0x43ce9e:
            events.append(('simple', machine.reg_read(reg.UC_ARM_REG_R0),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R1)),
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R2)),
                           machine.reg_read(reg.UC_ARM_REG_R3)))
            machine.reg_write(reg.UC_ARM_REG_PC, machine.reg_read(reg.UC_ARM_REG_LR))
        elif pc == RET:
            machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(reg.UC_ARM_REG_SP, SP)
    cpu.reg_write(reg.UC_ARM_REG_LR, RET | 1)
    cpu.reg_write(reg.UC_ARM_REG_R0, offset)
    cpu.reg_write(reg.UC_ARM_REG_R1, size)
    cpu.emu_start(entry | 1, RET + 2, count=5000)
    assert cpu.reg_read(reg.UC_ARM_REG_PC) == RET
    assert cpu.reg_read(reg.UC_ARM_REG_SP) == SP
    return {'result': cpu.reg_read(reg.UC_ARM_REG_R0), 'events': events}

cases = 0
offsets = (0, 1, 0x1000, 0x1ff0000, 0x2000000, 0x2001000,
           0x7ffff000, 0x80000000, 0xfffff000)
sizes = (0, 1, 4095, 4096, 4097, 8192, 8193, 0xffffffff)
for offset, size, flags, fail_at in itertools.product(offsets, sizes,
                                                      (0, 1, 2, 3, 4, 7),
                                                      (None, 0, 1)):
    original = run(0x540f84, offset, size, flags, fail_at)
    source = run(entry_source, offset, size, flags, fail_at)
    assert original == source, (offset, size, flags, fail_at, original, source)
    cases += 1
result = {'status': 'PASS_MAIN_NORFLASH_ERASE_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': hashlib.sha256(stock).hexdigest(),
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Physical sector erase, extended formatter and simple logger are injected equally; only the adapter path is compared.',
                     'Source strings are compared by content while linked addresses differ.',
                     'The finite offset, size, flag and failure-position matrix does not prove hardware behavior or all 32-bit loop cases.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], cases)
