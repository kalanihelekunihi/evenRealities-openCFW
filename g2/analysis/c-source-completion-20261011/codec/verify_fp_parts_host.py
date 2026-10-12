#!/usr/bin/env python3
"""Independent host IEEE checks for the native XIP part helpers.

These are mathematical checks of C candidates, not stock C-SKY execution.
"""
import ctypes
import hashlib
import json
import math
import random
import struct
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate/resident_xip_fp_parts.c'
MASK64 = (1 << 64) - 1


def expected_parts(bits):
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7ff
    fraction = bits & ((1 << 52) - 1)
    parts = [0xa5a5a5a5] * 5
    parts[1] = sign
    if exponent == 0:
        if fraction == 0:
            parts[0] = 2
        else:
            top = fraction.bit_length() - 1
            mantissa = (fraction << (60 - top)) & MASK64
            parts[0] = 3
            parts[2] = (top - 1074) & 0xffffffff
            parts[3] = mantissa & 0xffffffff
            parts[4] = mantissa >> 32
    elif exponent == 0x7ff:
        if fraction == 0:
            parts[0] = 4
        else:
            mantissa = (fraction << 8) & MASK64
            parts[0] = 1 if fraction & (1 << 51) else 0
            parts[3] = mantissa & 0xffffffff
            parts[4] = (mantissa >> 32) & ~(1 << 27)
    else:
        mantissa = ((1 << 52) | fraction) << 8
        parts[0] = 3
        parts[2] = (exponent - 1023) & 0xffffffff
        parts[3] = mantissa & 0xffffffff
        parts[4] = mantissa >> 32
    return parts


with tempfile.TemporaryDirectory() as temporary:
    binary = Path(temporary) / 'parts.so'
    subprocess.run(['cc', '-std=c11', '-O2', '-shared', '-fPIC',
                    str(SOURCE), '-o', str(binary)], check=True)
    library = ctypes.CDLL(str(binary))
    unpack = library.gx8002_xip_unpack_double_1020a704
    unpack.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(ctypes.c_uint32)]
    compare = library.gx8002_xip_fpcmp_parts_1020a7e8
    compare.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32)]
    compare.restype = ctypes.c_int32

    def native_parts(bits):
        words = (ctypes.c_uint32 * 2)(bits & 0xffffffff, bits >> 32)
        parts = (ctypes.c_uint32 * 5)(*[0xa5a5a5a5] * 5)
        unpack(words, parts)
        return parts

    unpack_rng = random.Random(0x1020a704)
    unpack_cases = [0, 1, (1 << 52) - 1, 1 << 52, 0x7ff << 52,
                    (0x7ff << 52) | 1, (0x7ff << 52) | (1 << 51), 1 << 63]
    unpack_cases += [unpack_rng.getrandbits(64) for _ in range(100000)]
    for bits in unpack_cases:
        assert list(native_parts(bits)) == expected_parts(bits), hex(bits)

    compare_rng = random.Random(0x1020a7e8)
    compare_cases = [(0, 1 << 63), (0x7ff << 52, MASK64),
                     ((0x7ff << 52) | 1, 0), (0x7ff << 52, 0),
                     (0xfff << 52, 0), (1, 2), (1 << 52, 2 << 52)]
    compare_cases += [(compare_rng.getrandbits(64),
                       compare_rng.getrandbits(64)) for _ in range(100000)]
    for a, b in compare_cases:
        left = struct.unpack('<d', a.to_bytes(8, 'little'))[0]
        right = struct.unpack('<d', b.to_bytes(8, 'little'))[0]
        expected = 1 if math.isnan(left) or math.isnan(right) else (
            (left > right) - (left < right))
        assert compare(native_parts(a), native_parts(b)) == expected, (
            hex(a), hex(b))

    receipt = {
        'scope': 'host IEEE classification/ordering only; stock C-SKY unqualified',
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'unpack_cases': len(unpack_cases),
        'compare_cases': len(compare_cases),
        'result': 'PASS',
    }
    (HERE / 'fp-parts-host-receipt.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
