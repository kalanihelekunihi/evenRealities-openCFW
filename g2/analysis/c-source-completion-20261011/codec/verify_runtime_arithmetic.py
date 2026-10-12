#!/usr/bin/env python3
"""Reproducible host arithmetic check for two native C candidate bodies.

This checks mathematical outputs, not C-SKY execution or byte equality.
"""
import ctypes
import hashlib
import json
import random
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate'
MASK64 = (1 << 64) - 1


def check_multiply(shared):
    fn = shared.__muldi3
    fn.argtypes = [ctypes.c_uint64, ctypes.c_uint64]
    fn.restype = ctypes.c_uint64
    rng = random.Random(0x1020a528)
    cases = [(0, 0), (1, 1), (MASK64, MASK64),
             (1 << 32, 1 << 32), (MASK64, 2),
             (0xffff0001, 0xffff0001)]
    cases.extend((rng.getrandbits(64), rng.getrandbits(64))
                 for _ in range(100000))
    for a, b in cases:
        assert fn(a, b) == (a * b) & MASK64, (a, b)
    return len(cases)


def check_division(shared):
    fn = shared.gx8002_xip_div64_102098b4
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
    fn.restype = ctypes.c_uint32
    rng = random.Random(0x102098b4)
    cases = [(0, 1), (MASK64, 1), (MASK64, (1 << 32) - 1),
             (1 << 32, 2), (MASK64, (1 << 31) + 1)]
    cases.extend((rng.getrandbits(64), rng.randrange(1, 1 << 32))
                 for _ in range(100000))
    for dividend, divisor in cases:
        words = (ctypes.c_uint32 * 2)(dividend & 0xffffffff,
                                      dividend >> 32)
        remainder = fn(words, divisor)
        quotient = words[0] | (words[1] << 32)
        assert (quotient, remainder) == divmod(dividend, divisor), (
            dividend, divisor)
    return len(cases)


with tempfile.TemporaryDirectory() as temporary:
    binary = Path(temporary) / 'arithmetic.so'
    paths = [SOURCE / 'resident_xip_muldi3.c',
             SOURCE / 'resident_xip_div64.c']
    subprocess.run(['cc', '-std=c11', '-O2', '-shared', '-fPIC',
                    *map(str, paths), '-o', str(binary)], check=True)
    library = ctypes.CDLL(str(binary))
    report = {
        'scope': 'host modulo arithmetic only; stock C-SKY runtime unqualified',
        'sources_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(
            p.read_bytes()).hexdigest() for p in paths},
        'muldi3_cases': check_multiply(library),
        'div64_nonzero_divisor_cases': check_division(library),
        'result': 'PASS',
    }
    (HERE / 'runtime-arithmetic-host-receipt.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
