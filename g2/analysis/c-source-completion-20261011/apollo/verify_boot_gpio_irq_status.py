#!/usr/bin/env python3
"""Bounded original/current-source GPIO status and PRIMASK oracle."""
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
ELF = HERE / 'boot-coplacement-gpio-primask-round/boot.elf'
OUT = HERE / 'boot-gpio-status-current-oracle.json'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s.data()]
    names = {sym.name: sym['st_value'] for sec in elf.iter_sections()
             if sec.header.sh_type == 'SHT_SYMTAB' for sym in sec.iter_symbols()}


def u32(cpu, address):
    return struct.unpack('<I', cpu.mem_read(address, 4))[0]


def put(cpu, address, value):
    cpu.mem_write(address, struct.pack('<I', value))


def run(stock, irq, enabled, primask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for start, size in ((0x410000, 0x30000), (0x20000000, 0x20000),
                        (0x40010000, 0x10000), (0x600000, 0x1000)):
        cpu.mem_map(start, size)
    if stock:
        cpu.mem_write(0x410000, blob)
    else:
        for start, data in segments:
            if 0x410000 <= start < 0x440000:
                cpu.mem_write(start, data)
    for bank in range(2):
        for group in range(7):
            base = 0x40010530 + bank * 0x70 + group * 0x10
            put(cpu, base, 0x3c00f00f ^ (bank << 20) ^ group)
            put(cpu, base + 4, 0xf0f0ff0f ^ (bank << 16) ^ group)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2001f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
    cpu.reg_write(A.UC_ARM_REG_PRIMASK, primask)
    cpu.reg_write(A.UC_ARM_REG_R0, irq)
    cpu.reg_write(A.UC_ARM_REG_R1, enabled)
    cpu.reg_write(A.UC_ARM_REG_R2, 0x20001000)
    put(cpu, 0x20001000, 0xa55aa55a)
    done = []
    visited = set()

    def hook(c, pc, size, _):
        if pc == 0x600000:
            done.append(True)
            c.emu_stop()
        elif stock and pc == 0x41b8ec:
            c.reg_write(A.UC_ARM_REG_R0, c.reg_read(A.UC_ARM_REG_PRIMASK))
            c.reg_write(A.UC_ARM_REG_PRIMASK, 1)
            c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
        elif stock and pc == 0x41dfbc:
            c.reg_write(A.UC_ARM_REG_PRIMASK, c.reg_read(A.UC_ARM_REG_R0))
            c.reg_write(A.UC_ARM_REG_PC, (pc + size) | 1)
        elif not stock and pc == 0x418b58:
            c.reg_write(A.UC_ARM_REG_IP, c.reg_read(A.UC_ARM_REG_PRIMASK))
            c.reg_write(A.UC_ARM_REG_PRIMASK, 1)
            c.reg_write(A.UC_ARM_REG_PC, (pc + 6) | 1)
        elif not stock and pc == 0x418b74:
            c.reg_write(A.UC_ARM_REG_PRIMASK, c.reg_read(A.UC_ARM_REG_IP))
            c.reg_write(A.UC_ARM_REG_PC, (pc + size) | 1)
        if stock and 0x41df48 <= pc < 0x41dfc6:
            visited.update(range(pc, pc + size))

    cpu.hook_add(UC_HOOK_CODE, hook)
    start = 0x41df48 if stock else names['opencfw_boot_gpio_irq_status'] & ~1
    try:
        cpu.emu_start(start | 1, 0x600002, count=2000)
    except Exception as error:
        raise RuntimeError((stock, irq, enabled, primask,
                            hex(cpu.reg_read(A.UC_ARM_REG_PC)))) from error
    assert done, (stock, irq, enabled)
    return (cpu.reg_read(A.UC_ARM_REG_R0), u32(cpu, 0x20001000),
            cpu.reg_read(A.UC_ARM_REG_PRIMASK)), visited


cases = []
visited = set()
for irq in (55, 56, 62, 63, 124, 125, 131, 132):
    for enabled in (0, 1):
        for primask in (0, 1):
            original, hit = run(True, irq, enabled, primask)
            candidate, _ = run(False, irq, enabled, primask)
            assert original == candidate, (irq, enabled, primask, original, candidate)
            visited |= hit
            cases.append({'irq': irq, 'enabled': enabled, 'initial_primask': primask,
                          'return': original[0], 'output': original[1],
                          'final_primask': original[2]})
result = {'status': 'PASS', 'stock_sha256': hashlib.sha256(blob).hexdigest(),
          'selected_source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'selected_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'cases': cases, 'body_bytes': 126,
          'visited_body_bytes': len(visited & set(range(0x41df48, 0x41dfc6))),
          'limits': ['Synthetic MMIO registers and Cortex-M CPU; no real GPIO interrupt or hardware proof.',
                     'Samples bank edges, enable modes and initial PRIMASK, not all possible IRQ arguments.']}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cases), result['visited_body_bytes'])
