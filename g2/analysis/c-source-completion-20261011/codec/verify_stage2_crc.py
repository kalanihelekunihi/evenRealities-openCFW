#!/usr/bin/env python3
"""Validate semantic stock CRC table and bounded source behavior."""
import ctypes
import hashlib
import json
import pathlib
import random
import struct
import subprocess
import tempfile
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/uart_stage2.bin'
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate/uart_stage2_crc.c'
blob = IMAGE.read_bytes(); base = 0x10002800
stock = blob[0x10008688-base:0x10008688-base+1024]
values = []
for i in range(256):
    v = i
    for _ in range(8):
        v = (v >> 1) ^ (0xedb88320 if v & 1 else 0)
    values.append(v)
assert struct.pack('<256I', *values) == stock
with tempfile.TemporaryDirectory() as tmp:
    library = pathlib.Path(tmp) / 'crc.so'
    subprocess.run(['clang', '-std=c11', '-O2', '-shared', '-fPIC', str(SOURCE), '-o', str(library)], check=True)
    f = ctypes.CDLL(str(library)).gx8002_uart_stage2_checksum_66b8
    f.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
    f.restype = ctypes.c_uint32
    rng = random.Random(0x66b8)
    mismatches = []
    total = 0
    for length in list(range(33)) + [63, 64, 65, 127, 128, 129, 255, 256, 257, 1024]:
        for seed in [0, 1, 0xffffffff, rng.getrandbits(32)]:
            data = rng.randbytes(length)
            buf = ctypes.create_string_buffer(data or b'\0')
            actual = f(seed, ctypes.addressof(buf), length)
            expected = zlib.crc32(data, seed)
            total += 1
            if actual != expected:
                mismatches.append({'length': length, 'seed': seed, 'actual': actual, 'expected': expected})
    receipt = {'stock_image_sha256': hashlib.sha256(blob).hexdigest(),
               'stock_crc_table_sha256': hashlib.sha256(stock).hexdigest(),
               'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'cases': total, 'mismatches': mismatches,
               'qualification': 'exact native table bytes and bounded host C vs zlib; not C-SKY runtime'}
    target = pathlib.Path(__file__).with_name('stage2-crc-receipt.json')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'cases': total, 'mismatch_count': len(mismatches), 'receipt': str(target)}))
    if mismatches: raise SystemExit(1)
