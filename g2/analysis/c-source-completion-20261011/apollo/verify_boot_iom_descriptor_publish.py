#!/usr/bin/env python3
"""Bounded stock/current selected C IOM descriptor publish MMIO oracle."""
import hashlib
import json
import pathlib
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE = ROOT / 'g2/components/bootloader/initializer_callbacks/context_events.c'
ELF = HERE / 'boot-coplacement-stimer-ordered-round/boot.elf'
OUT = HERE / 'boot-iom-descriptor-publish-current-oracle.json'
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as fh:
    elf = ELFFile(fh)
    segments = [(seg['p_vaddr'], seg.data()) for seg in elf.iter_segments()
                if seg['p_type'] == 'PT_LOAD' and seg.data()]
    names = {sym.name: sym['st_value'] for sec in elf.iter_sections()
             if sec.header.sh_type == 'SHT_SYMTAB' for sym in sec.iter_symbols()}


def put(cpu, addr, value):
    cpu.mem_write(addr, struct.pack('<I', value & 0xffffffff))


def run(stock, module, ring_size, previous):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for base, size in ((0x410000, 0x30000), (0x20000000, 0x30000),
                       (0x40050000, 0x20000), (0x600000, 0x1000)):
        cpu.mem_map(base, size)
    if stock:
        cpu.mem_write(0x410000, blob)
    else:
        for base, payload in segments:
            if 0x410000 <= base < 0x440000:
                cpu.mem_write(base, payload)
    handle = 0x20001000
    records = 0x20005000
    put(cpu, handle + 4, module)
    put(cpu, handle + 0x848, ring_size)
    put(cpu, handle + 0x850, previous)
    put(cpu, handle + 0x854, records)
    for index in range(8):
        for word in range(8):
            put(cpu, records + index * 32 + word * 4,
                0x12000000 | index << 12 | word << 4 | (module & 15))
    cpu.reg_write(A.UC_ARM_REG_SP, 0x2002f000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
    cpu.reg_write(A.UC_ARM_REG_R0, handle)
    writes, done, visited = [], [], set()

    def memory(c, access, address, size, value, _):
        if 0x40050000 <= address < 0x40070000:
            writes.append((hex(address), value & 0xffffffff))

    def code(c, pc, size, _):
        if pc == 0x600000:
            done.append(True)
            c.emu_stop()
        if stock and 0x42c45a <= pc < 0x42c4c6:
            visited.update(range(pc, pc + size))

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, memory)
    entry = 0x42c45a if stock else names['opencfw_boot_iom_descriptor_publish'] & ~1
    cpu.emu_start(entry | 1, 0x600002, count=1000)
    assert done, (stock, module, ring_size, previous)
    return (writes, bytes(cpu.mem_read(handle, 0x858)),
            bytes(cpu.mem_read(records, 256))), visited


cases, visited = [], set()
for module in (0, 1, 2):
    for ring_size, previous in ((0, 0), (0, 3), (1, 0), (4, 0),
                                (4, 3), (4, 0xffffffff)):
        original, hit = run(True, module, ring_size, previous)
        candidate, _ = run(False, module, ring_size, previous)
        assert original == candidate, (module, ring_size, previous,
                                       original[0], candidate[0])
        visited |= hit
        cases.append({'module': module, 'ring_size': ring_size,
                      'previous': previous, 'ordered_writes': original[0]})
result = {'status': 'PASS', 'stock_sha256': hashlib.sha256(blob).hexdigest(),
          'selected_source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'selected_elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
          'cases': cases, 'body_bytes': 108,
          'visited_body_bytes': len(visited & set(range(0x42c45a, 0x42c4c6))),
          'limits': ['Synthetic descriptor ring and MMIO, no physical IOM transfer or DMA proof.',
                     'Fixture covers three module bases and six ring states; no concurrent mutation.']}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cases), result['visited_body_bytes'])
