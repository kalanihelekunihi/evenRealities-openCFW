#!/usr/bin/env python3
"""Compare stock and source FAL read/write outer paths with the same lowers."""
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
BUFFER = 0x20001000
specs = [
    ('read', 0x540ed4, 'g2_norflash_read_540ed4', 0x4709c8),
    ('write', 0x540f2c, 'g2_norflash_write_540f2c', 0x4708a8),
]

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
    symbols = {item.name: item['st_value'] & ~1 for item in
               elf.get_section_by_name('.symtab').iter_symbols() if item.name}

def cstring(cpu, address):
    data = bytearray()
    while len(data) < 256:
        value = cpu.mem_read(address + len(data), 1)[0]
        if value == 0:
            return data.decode()
        data.append(value)
    raise AssertionError('unterminated string')

def run(label, entry, lower, lower_result, flags, size):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x430000, 0x380000)
    cpu.mem_write(BASE, stock)
    cpu.mem_map(0x800000, 0x10000)
    for address, data in segments:
        cpu.mem_write(address, data)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_write(BUFFER, b'\x5a' * 32)
    events = []
    def hook(machine, pc, insn_size, unused):
        if pc == lower:
            events.append(('lower', machine.reg_read(reg.UC_ARM_REG_R0),
                           machine.reg_read(reg.UC_ARM_REG_R1), machine.reg_read(reg.UC_ARM_REG_R2)))
            machine.reg_write(reg.UC_ARM_REG_R0, lower_result)
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
                           cstring(machine, machine.reg_read(reg.UC_ARM_REG_R3)), line,
                           cstring(machine, fmt)))
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
    cpu.reg_write(reg.UC_ARM_REG_R0, 0x1fc1234)
    cpu.reg_write(reg.UC_ARM_REG_R1, BUFFER)
    cpu.reg_write(reg.UC_ARM_REG_R2, size)
    cpu.emu_start(entry | 1, RET + 2, count=2000)
    assert cpu.reg_read(reg.UC_ARM_REG_PC) == RET
    assert cpu.reg_read(reg.UC_ARM_REG_SP) == SP
    return {'result': cpu.reg_read(reg.UC_ARM_REG_R0), 'events': events}

cases = 0
for label, native, symbol, lower in specs:
    for outcome, flags, size in itertools.product((0, 1, 5, 0xffffffff),
                                                   (0, 1, 2, 3, 4, 5, 6, 7, 255),
                                                   (0, 1, 255, 256, 0x10000,
                                                    0x80000000, 0xffffffff)):
        original = run(label, native, lower, outcome, flags, size)
        source = run(label, symbols[symbol], lower, outcome, flags, size)
        assert original == source, (label, outcome, flags, size, original, source)
        cases += 1
result = {'status': 'PASS_MAIN_NORFLASH_RW_BOUNDED_NATIVE_SOURCE',
          'cases': cases, 'stock_sha256': hashlib.sha256(stock).hexdigest(),
          'source_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
          'limits': ['Physical flash lowers, logger formatting/output and real hardware are injected equally; only the adapter outer paths are compared.',
                     'Source product strings are compared by contents while their linked addresses differ.',
                     'Only the enumerated lower results, flags and request sizes are covered.']}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'], cases)
