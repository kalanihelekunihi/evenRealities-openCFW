#!/usr/bin/env python3
"""Differential checks of compiled C against authenticated R1 Thumb routines.
Requires Unicorn (2.1.4 used by the recorded run). Never executes device I/O.
"""
import ctypes
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unicorn
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_LR, UC_ARM_REG_SP, UC_ARM_REG_PC
from generate_stock_checksum_tables import tables, render

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / 'r1/blobs/official/r1-2.2.6.0009/application.bin'
EXPECTED = '0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'


def main():
    image = APP.read_bytes()
    assert len(image) == 646408 and hashlib.sha256(image).hexdigest() == EXPECTED
    assert (ROOT / 'r1/source/stock_checksum_tables.inc').read_text() == render()
    table_receipts = []
    for literal, width, values in zip((0x5d8a0, 0x5d8c8), (16, 32), tables()):
        address = struct.unpack_from('<I', image, literal - 0x27000)[0]
        expected = struct.pack('<' + ('H' if width == 16 else 'I') * 256, *values)
        assert image[address - 0x27000:address - 0x27000 + len(expected)] == expected
        table_receipts.append(dict(address=hex(address), bytes=len(expected),
                                   sha256=hashlib.sha256(expected).hexdigest()))
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x20000, 0xc0000)
    uc.mem_write(0x27000, image)
    uc.mem_map(0x20000000, 0x10000)
    stop, buffer, state = 0x20000100, 0x20001000, 0x2000e000
    uc.mem_write(stop, b'\x00\xbe')

    def stock(entry, payload, seed=0):
        uc.mem_write(buffer, payload or b'\0')
        uc.mem_write(state, struct.pack('<I', seed))
        for register, value in ((UC_ARM_REG_R0, buffer), (UC_ARM_REG_R1, len(payload)),
                                (UC_ARM_REG_R2, state), (UC_ARM_REG_SP, 0x2000f000),
                                (UC_ARM_REG_LR, stop | 1)):
            uc.reg_write(register, value)
        uc.emu_start(entry | 1, stop, count=1000000)
        assert uc.reg_read(UC_ARM_REG_PC) == stop, 'stock routine did not return within instruction budget'
        return (struct.unpack('<I', uc.mem_read(state, 4))[0] if entry == 0x5d8a4
                else uc.reg_read(UC_ARM_REG_R0))

    with tempfile.TemporaryDirectory(prefix='r1-checksums-') as temporary:
        library = Path(temporary) / 'checksums.dylib'
        command = ['clang', '-shared', '-fPIC', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                   '-I' + str(ROOT / 'r1/source/include'),
                   str(ROOT / 'r1/source/stock_checksums.c'), str(ROOT / 'r1/source/r1_crc.c'),
                   '-o', str(library)]
        subprocess.run(command, check=True)
        c = ctypes.CDLL(str(library))
        c.r1_stock_crc16_modbus.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        c.r1_stock_crc16_modbus.restype = ctypes.c_uint16
        c.r1_stock_crc32_update.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        c.r1_stock_hash131.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        c.r1_stock_hash131.restype = ctypes.c_uint32
        c.r1_crc32_castagnoli_update.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_size_t]
        c.r1_crc32_castagnoli_update.restype = ctypes.c_uint32
        rng = random.Random(0x2260009)
        cases = [b'', b'123456789', bytes(range(256)), bytes(4096)]
        cases += [bytes(rng.randrange(256) for _ in range(rng.randrange(1025))) for _ in range(128)]
        checks = 0
        for payload in cases:
            assert c.r1_stock_crc16_modbus(payload, len(payload)) == stock(0x5d87c, payload)
            assert c.r1_stock_hash131(payload, len(payload)) == stock(0x5d8cc, payload)
            checks += 2
            for seed in (0, 0xffffffff, rng.getrandbits(32)):
                result = ctypes.c_uint32(seed)
                c.r1_stock_crc32_update(payload, len(payload), ctypes.byref(result))
                actual = stock(0x5d8a4, payload, seed)
                assert result.value == actual
                assert c.r1_crc32_castagnoli_update(seed, payload, len(payload)) == actual
                checks += 2
    bodies = []
    for entry, size in ((0x5d87c, 36), (0x5d8a4, 34), (0x5d8cc, 26)):
        bodies.append(dict(entry=hex(entry), bytes=size, sha256=hashlib.sha256(
            image[entry - 0x27000:entry - 0x27000 + size]).hexdigest()))
    receipt = dict(application_sha256=EXPECTED, unicorn_version=unicorn.__version__,
                   seed='0x2260009', payloads=len(cases), comparisons=checks,
                   tables=table_receipts, bodies=bodies,
                   source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (ROOT / 'r1/source').rglob('*') if p.is_file()},
                   scope='host-compiled C against stock Thumb; ARM candidate objects compile separately',
                   instruction_identity=False, whole_image_link=False)
    output = ROOT / 'r1/research/source-build/checksum-verification.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'{checks} comparisons passed against three authenticated stock routines; both tables match')


if __name__ == '__main__':
    main()
