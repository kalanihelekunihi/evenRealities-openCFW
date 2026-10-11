#!/usr/bin/env python3
"""Compare the authenticated Boot assert semihost call and abort path."""
from pathlib import Path
import json
import struct
import sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP)

ROOT = Path(__file__).resolve().parents[4]
ELF = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'g2/analysis/c-source-completion-20261011/apollo/boot-coplacement-assert/boot.elf'
STOCK = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
LFS = (ROOT / 'g2/components/bootloader/filesystem/upstream/lfs.c').read_text()
native_file_address = struct.unpack_from('<I', STOCK, 0x41129c-0x410000)[0]
native_condition_address = struct.unpack_from('<I', STOCK, 0x4112a8-0x410000)[0]
native_second_condition_address = struct.unpack_from('<I', STOCK, 0x4112a4-0x410000)[0]
def stock_string(address):
    return STOCK[address-0x410000:].split(b'\0',1)[0]
assert stock_string(native_file_address) == b'D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c'
assert stock_string(native_condition_address) == b'pcache->block < lfs->block_count'
assert stock_string(native_second_condition_address) == b'err <= 0'
assert LFS.splitlines()[178].strip() == 'LFS_ASSERT(pcache->block < lfs->block_count);'
assert LFS.splitlines()[182].strip() == 'LFS_ASSERT(err <= 0);'
with ELF.open('rb') as stream:
    elf = ELFFile(stream)
    image = next(p.data() for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD' and p['p_vaddr'] == 0x410000)
    symbols = {s.name: s['st_value'] & ~1 for s in elf.get_section_by_name('.symtab').iter_symbols()}
assert stock_string(native_file_address)+b'\0' in image
assert stock_string(native_condition_address)+b'\0' in image
assert stock_string(native_second_condition_address)+b'\0' in image

def run(native, status):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x410000, 0x40000)
    cpu.mem_write(0x410000, STOCK if native else image)
    cpu.mem_map(0x20000000, 0x30000)
    cpu.mem_map(0x500000, 0x1000)
    stack = 0x2002f000
    cpu.reg_write(UC_ARM_REG_R0, 0x500100)
    cpu.reg_write(UC_ARM_REG_R1, 0x500180)
    cpu.reg_write(UC_ARM_REG_R2, 179)
    cpu.reg_write(UC_ARM_REG_SP, stack)
    cpu.reg_write(UC_ARM_REG_LR, 0x500801)
    entry = 0x415734 if native else symbols['opencfw_boot_assert_report']
    observations = []
    def on_code(emu, address, _size, _data):
        if bytes(emu.mem_read(address, 2)) != b'\xab\xbe':
            return
        r0 = emu.reg_read(UC_ARM_REG_R0)
        r1 = emu.reg_read(UC_ARM_REG_R1)
        r2 = emu.reg_read(UC_ARM_REG_R2)
        sp = emu.reg_read(UC_ARM_REG_SP)
        arg = bytes(emu.mem_read(r2, 12)) if r2 == stack - 16 else None
        observations.append((r0, r1, r2 == stack - 16, arg))
        emu.emu_stop()
    cpu.hook_add(UC_HOOK_CODE, on_code)
    start = entry | 1
    for _ in range(4):
        cpu.emu_start(start, 0x500800, count=100)
        if cpu.reg_read(UC_ARM_REG_PC) == 0x500800:
            break
        if not observations:
            raise AssertionError('No BKPT reached')
        cpu.reg_write(UC_ARM_REG_R0, status if len(observations) == 1 else 0)
        start = cpu.reg_read(UC_ARM_REG_PC) + 3
    return observations, cpu.reg_read(UC_ARM_REG_SP)

cases = []
for status in (0, 1, 0xffffffff):
    stock = run(True, status)
    source = run(False, status)
    assert stock == source, (status, stock, source)
    cases.append({'status': status, 'semihost_calls': len(stock[0]), 'returned_sp': stock[1]})
print(json.dumps({'status': 'PASS_BOOT_ASSERT_NATIVE_SOURCE', 'cases': cases}))
