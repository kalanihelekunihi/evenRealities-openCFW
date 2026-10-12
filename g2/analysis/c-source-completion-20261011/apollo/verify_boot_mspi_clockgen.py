#!/usr/bin/env python3
"""Bounded stock/current selected C MSPI clockgen register and ABI oracle."""
import hashlib
import json
import pathlib
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c'
ELF = HERE / 'boot-coplacement-mspi-clockgen-ordered-round/boot.elf'
OUT = HERE / 'boot-mspi-clockgen-current-oracle.json'
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


def run(stock, module, enable, configure, source, primask):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for start, size in ((0x410000, 0x30000), (0x20000000, 0x20000),
                        (0x40004000, 0x1000), (0x600000, 0x1000)):
        cpu.mem_map(start, size)
    if stock:
        cpu.mem_write(0x410000, blob)
    else:
        for start, data in segments:
            if 0x410000 <= start < 0x440000:
                cpu.mem_write(start, data)
    put(cpu, 0x40004110, 0xa55a3cc3)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2001f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
    cpu.reg_write(A.UC_ARM_REG_PRIMASK, primask)
    for reg, val in ((A.UC_ARM_REG_R0, module), (A.UC_ARM_REG_R1, enable),
                     (A.UC_ARM_REG_R2, configure), (A.UC_ARM_REG_R3, source)):
        cpu.reg_write(reg, val)
    done = []
    visited = set()
    events = []

    def memory(c, access, address, size, value, _):
        if address == 0x40004110:
            events.append(('read' if access == 16 else 'write', value & 0xffffffff))

    def code(c, pc, size, _):
        if pc == 0x600000:
            done.append(True)
            c.emu_stop()
        elif stock and pc == 0x41b8ec:
            c.reg_write(A.UC_ARM_REG_R0, c.reg_read(A.UC_ARM_REG_PRIMASK))
            c.reg_write(A.UC_ARM_REG_PRIMASK, 1)
            c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
        elif stock and pc == 0x424a12:
            c.reg_write(A.UC_ARM_REG_PRIMASK, c.reg_read(A.UC_ARM_REG_R0))
            c.reg_write(A.UC_ARM_REG_PC, (pc + size) | 1)
        elif not stock and pc == 0x4209ca:
            c.reg_write(A.UC_ARM_REG_R4, c.reg_read(A.UC_ARM_REG_PRIMASK))
            c.reg_write(A.UC_ARM_REG_PRIMASK, 1)
            c.reg_write(A.UC_ARM_REG_PC, (pc + 6) | 1)
        elif not stock and pc == 0x420a36:
            c.reg_write(A.UC_ARM_REG_PRIMASK, c.reg_read(A.UC_ARM_REG_R4))
            c.reg_write(A.UC_ARM_REG_PC, (pc + size) | 1)
        elif (stock and pc == 0x41d1c0) or (not stock and pc == names['opencfw_hal_delay_us'] & ~1):
            events.append(('delay', c.reg_read(A.UC_ARM_REG_R0)))
            c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
        if stock and 0x4249a0 <= pc < 0x424a18:
            visited.update(range(pc, pc + size))

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_READ, memory)
    cpu.hook_add(UC_HOOK_MEM_WRITE, memory)
    start = 0x4249a0 if stock else names['opencfw_bl_mspi_clockgen_control'] & ~1
    cpu.emu_start(start | 1, 0x600002, count=3000)
    assert done, (stock, module, enable, configure, source)
    return (cpu.reg_read(A.UC_ARM_REG_R0), u32(cpu, 0x40004110),
            cpu.reg_read(A.UC_ARM_REG_PRIMASK), events), visited


cases = []
visited = set()
for module in (0, 1, 5, 6, 7, 51, 52, 256, 0x80000000):
    for enable, configure, source, primask in ((0, 0, 0x12345678, 0),
                                                (0, 1, 0xff000003, 1),
                                                (1, 0, 0x12345678, 0),
                                                (1, 1, 0xff000003, 1)):
        original, hit = run(True, module, enable, configure, source, primask)
        candidate, _ = run(False, module, enable, configure, source, primask)
        assert original == candidate, (module, enable, configure, source,
                                       primask, original, candidate)
        visited |= hit
        cases.append({'module': module, 'enable': enable, 'configure': configure,
                      'source': source, 'initial_primask': primask,
                      'return': original[0], 'register': original[1],
                      'final_primask': original[2], 'events': original[3]})
result = {'status': 'PASS', 'stock_sha256': hashlib.sha256(blob).hexdigest(),
          'selected_source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'selected_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'cases': cases, 'body_bytes': 120,
          'visited_body_bytes': len(visited & set(range(0x4249a0, 0x424a18))),
          'limits': ['Synthetic MMIO and cut critical/delay instructions; no hardware clock proof.',
                     'Discrete module/configuration cases; not exhaustive 32-bit argument domain.']}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cases), result['visited_body_bytes'])
