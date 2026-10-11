#!/usr/bin/env python3
"""Compare the complete stock FlashDB KV-cache update with source C."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/main/flashdb_cache_update_candidates_20261010/cache_update.c'
BLOB = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(BLOB).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
CC = subprocess.check_output(['xcrun', '--find', 'clang'], text=True).strip()
ELF = HERE / 'flashdb-cache-update.elf'
CMD = [CC, '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-Oz',
       '-std=c11', '-ffreestanding', '-fno-builtin', '-nostdlib',
       '-Wl,-Ttext=0x10001000', '-Wl,-e,g2_flashdb_cache_update',
       '-Wl,--defsym=g2_flashdb_crc32=0x585841', str(SOURCE), '-o', str(ELF)]
subprocess.run(CMD, check=True, capture_output=True)
with ELF.open('rb') as f:
    e = ELFFile(f)
    ENTRY = next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()
                 if s.name == 'g2_flashdb_cache_update')
    SEGS = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

DB, NAME, SP = 0x20050000, 0x20051000, 0x200ff000
CRC = 0x7777

def fixture(mode, index, activity):
    db = bytearray(b'\xa5' * 2304)
    for i in range(64):
        addr = 0x10000 + i
        crc = i
        active = 5
        if mode == 'empty' and i == index: addr = 0xffffffff
        if mode in ('match', 'delete') and i == index: crc = CRC
        if mode == 'evict' and i == index: active = activity
        if mode == 'decay' and i == index: active = activity
        struct.pack_into('<HHI', db, 168 + 8 * i, crc, active, addr)
    return bytes(db)

def run(source, before, addr, length):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x437000, ((len(BLOB) + 0xfe0 + 0xfff) // 0x1000) * 0x1000)
    u.mem_write(0x437fe0, BLOB)
    u.mem_map(0x10000000, 0x100000)
    for a, b in SEGS: u.mem_write(a, b)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(DB, before)
    u.mem_write(NAME, b'name')
    for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                          (DB, NAME, length, addr)): u.reg_write(reg, value)
    u.reg_write(UC_ARM_REG_SP, SP)
    u.reg_write(UC_ARM_REG_LR, 0x10000001)
    calls = []
    def hook(emu, pc, size, _):
        if pc == 0x585840:
            args = tuple(emu.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            assert args == (0, NAME, length), (source, args)
            calls.append(args)
            emu.reg_write(UC_ARM_REG_R0, CRC << 16)
            emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start((ENTRY if source else 0x543d1d), 0x10000000, count=20000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x10000000
    assert u.reg_read(UC_ARM_REG_SP) == SP
    assert calls == [(0, NAME, length)]
    return bytes(u.mem_read(DB, len(before)))

cases = []
for mode, index, activity, addr, length in itertools.product(
        ('match', 'delete', 'empty', 'evict', 'decay', 'full'),
        (0, 1, 31, 63), (0, 1, 0xffff), (0x12345678, 0xffffffff), (0, 4, 63)):
    before = fixture(mode, index, activity)
    # The delete path is defined by the incoming sentinel; the rest exercise both
    # sentinel and live addresses to test stock precedence with coherent RAM.
    a = run(False, before, addr, length)
    b = run(True, before, addr, length)
    if a != b:
        delta = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
        raise AssertionError((mode, index, activity, hex(addr), length, delta,
                              a[delta:delta+16].hex(), b[delta:delta+16].hex()))
    cases.append((mode, index, activity, addr, length))

receipt = {'status': 'PASS', 'cases': len(cases), 'stock_address': '0x543d1c..0x543e28',
           'stock_body_sha256': hashlib.sha256(BLOB[0x543d1c-0x437fe0:0x543e28-0x437fe0]).hexdigest(),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(), 'compile': CMD,
           'limits': 'Cortex-M4 scalar execution because Unicorn lacks some M55 instructions; M55 production compile is separate. Coherent synthetic 64-row database; CRC32 is a shared explicit callback returning 0x77770000. Does not prove database initialization, flash read or CRC provider source.'}
(HERE / 'cache-update-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS cache_update', len(cases))
