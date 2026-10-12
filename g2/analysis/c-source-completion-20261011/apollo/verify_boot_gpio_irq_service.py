#!/usr/bin/env python3
"""Bounded stock/current selected C GPIO callback dispatch oracle."""
import hashlib
import json
import pathlib
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/gpio_irq_runtime.c'
ELF = HERE / 'boot-coplacement-mspi-clockgen-ordered-round/boot.elf'
OUT = HERE / 'boot-gpio-service-current-oracle.json'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s.data()]
    names = {sym.name: sym['st_value'] for sec in elf.iter_sections()
             if sec.header.sh_type == 'SHT_SYMTAB' for sym in sec.iter_symbols()}


def put(cpu, address, value):
    cpu.mem_write(address, struct.pack('<I', value))


def run(stock, irq, status, absent):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for start, size in ((0x410000, 0x30000), (0x20000000, 0x30000),
                        (0x600000, 0x1000)):
        cpu.mem_map(start, size)
    if stock:
        cpu.mem_write(0x410000, blob)
    else:
        for start, data in segments:
            if 0x410000 <= start < 0x440000:
                cpu.mem_write(start, data)
    for index in range(14):
        for bit in range(32):
            address = index * 0x80 + bit * 4
            put(cpu, 0x20023600 + address, 0 if (absent and bit in (0, 31)) else 0x600101)
            put(cpu, 0x20023d00 + address, 0x3a000000 | index << 8 | bit)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2002f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
    cpu.reg_write(A.UC_ARM_REG_R0, irq)
    cpu.reg_write(A.UC_ARM_REG_R1, status)
    done = []
    calls = []
    visited = set()

    def hook(c, pc, size, _):
        if pc == 0x600000:
            done.append(True)
            c.emu_stop()
        elif pc == 0x600100:
            calls.append(c.reg_read(A.UC_ARM_REG_R0))
            c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
        if stock and 0x41e09a <= pc < 0x41e10e:
            visited.update(range(pc, pc + size))

    cpu.hook_add(UC_HOOK_CODE, hook)
    start = 0x41e09a if stock else names['opencfw_boot_gpio_irq_service'] & ~1
    cpu.emu_start(start | 1, 0x600002, count=2000)
    assert done, (stock, irq, status)
    return (cpu.reg_read(A.UC_ARM_REG_R0), calls), visited


cases = []
visited = set()
for irq in (55, 56, 62, 63, 124, 125, 131, 132):
    for status in (0, 1, 0x80000000, 0x80000005):
        for absent in (False, True):
            original, hit = run(True, irq, status, absent)
            candidate, _ = run(False, irq, status, absent)
            assert original == candidate, (irq, status, absent, original, candidate)
            visited |= hit
            cases.append({'irq': irq, 'status': status, 'absent_callbacks': absent,
                          'return': original[0], 'callback_arguments': original[1]})
result = {'status': 'PASS', 'stock_sha256': hashlib.sha256(blob).hexdigest(),
          'selected_source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'selected_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'cases': cases, 'body_bytes': 116,
          'visited_body_bytes': len(visited & set(range(0x41e09a, 0x41e10e))),
          'limits': ['Callback entries and arguments are synthetic; actual producer and interrupt delivery remain unqualified.',
                     'No physical GPIO or asynchronous callback proof.']}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cases), result['visited_body_bytes'])
