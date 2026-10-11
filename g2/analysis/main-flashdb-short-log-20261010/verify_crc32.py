#!/usr/bin/env python3
"""Compare source CRC-32 public entry with authenticated stock FlashDB."""
from pathlib import Path
import hashlib, itertools, json, random, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/main/flashdb_crc32_candidates_20261010/crc32.c'
BLOB = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(BLOB).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
CC = subprocess.check_output(['xcrun', '--find', 'clang'], text=True).strip()
ELF = HERE / 'flashdb-crc32.elf'
CMD = [CC, '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb', '-Oz',
       '-std=c11', '-ffreestanding', '-fno-builtin', '-nostdlib',
       '-Wl,-Ttext=0x10001000', '-Wl,-e,g2_flashdb_crc32', str(SOURCE), '-o', str(ELF)]
subprocess.run(CMD, check=True, capture_output=True)
with ELF.open('rb') as f:
    e = ELFFile(f)
    ENTRY = next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()
                 if s.name == 'g2_flashdb_crc32')
    SEGS = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def run(source, seed, data):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x437000, ((len(BLOB) + 0xfe0 + 0xfff) // 0x1000) * 0x1000)
    u.mem_write(0x437fe0, BLOB)
    u.mem_map(0x10000000, 0x100000)
    for a, b in SEGS: u.mem_write(a, b)
    u.mem_map(0x20000000, 0x100000)
    u.mem_write(0x20050000, data if data else b'\xa5')
    for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2),
                          (seed, 0x20050000, len(data))): u.reg_write(reg, value)
    u.reg_write(UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(UC_ARM_REG_LR, 0x10000001)
    u.emu_start(ENTRY if source else 0x585841, 0x10000000, count=500000)
    assert u.reg_read(UC_ARM_REG_PC) == 0x10000000
    assert u.reg_read(UC_ARM_REG_SP) == 0x200ff000
    return u.reg_read(UC_ARM_REG_R0)

rng = random.Random(0x714d6159)
cases = []
for size, seed in itertools.product((0, 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 256, 1024),
                                     (0, 1, 0x12345678, 0xffffffff)):
    for pattern in range(4):
        data = (bytes(size) if pattern == 0 else bytes([0xff])*size if pattern == 1
                else bytes(range(256))[:size] if pattern == 2 and size <= 256
                else bytes(rng.randrange(256) for _ in range(size)))
        a, b = run(False, seed, data), run(True, seed, data)
        assert a == b, (size, seed, pattern, hex(a), hex(b))
        cases.append((size, seed, pattern))
for data in (b'123456789', bytes(range(256)), bytes(rng.randrange(256) for _ in range(1024))):
    full = run(True, 0, data)
    for split in (0, 1, len(data)//2, len(data)):
        assert run(True, run(True, 0, data[:split]), data[split:]) == full
        assert run(False, run(False, 0, data[:split]), data[split:]) == full

receipt = {'status': 'PASS', 'cases': len(cases), 'stock_address': '0x585840..0x585870',
           'stock_body_sha256': hashlib.sha256(BLOB[0x585840-0x437fe0:0x585870-0x437fe0]).hexdigest(),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(), 'compile': CMD,
           'limits': 'Cortex-M55 source executed in Unicorn; stock table-backed function executed from fixed image. Deterministic buffers, seeds and chained updates; no hardware or database-state claim.'}
(HERE / 'crc32-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS CRC32', len(cases), 'plus chained updates')
