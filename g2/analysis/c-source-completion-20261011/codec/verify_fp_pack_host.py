#!/usr/bin/env python3
"""Host IEEE checks for source pack-double and unpack-double candidates."""
import ctypes
import hashlib
import json
import random
import struct
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate'
UNPACK = SOURCE / 'resident_xip_fp_parts.c'
PACK = SOURCE / 'resident_xip_pack_double.c'

with tempfile.TemporaryDirectory() as temporary:
    binary = Path(temporary) / 'pack.so'
    subprocess.run(['cc', '-std=c11', '-O2', '-shared', '-fPIC',
                    str(UNPACK), str(PACK), '-o', str(binary)], check=True)
    library = ctypes.CDLL(str(binary))
    unpack = library.gx8002_xip_unpack_double_1020a704
    unpack.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(ctypes.c_uint32)]
    pack = library.gx8002_xip_pack_double_1020a574
    pack.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    pack.restype = ctypes.c_uint64

    rng = random.Random(0x1020a574)
    roundtrips = [0, 1, (1 << 52) - 1, 1 << 52, 0x7ff << 52,
                  (0x7ff << 52) | 1, (0x7ff << 52) | (1 << 51), 1 << 63]
    roundtrips += [rng.getrandbits(64) for _ in range(100000)]
    for bits in roundtrips:
        words = (ctypes.c_uint32 * 2)(bits & 0xffffffff, bits >> 32)
        parts = (ctypes.c_uint32 * 5)()
        unpack(words, parts)
        exponent = (bits >> 52) & 0x7ff
        fraction = bits & ((1 << 52) - 1)
        expected = bits | ((1 << 51) if exponent == 0x7ff and fraction else 0)
        assert pack(parts) == expected, hex(bits)

    rational_rng = random.Random(0x1020a575)
    for index in range(20000):
        exponent = rational_rng.randrange(-1076, 1025)
        mantissa = (1 << 60) | rational_rng.getrandbits(60)
        sign = rational_rng.getrandbits(1)
        parts = (ctypes.c_uint32 * 5)(
            3, sign, exponent & 0xffffffff,
            mantissa & 0xffffffff, mantissa >> 32)
        exact = (Fraction(mantissa, 1 << (60 - exponent))
                 if exponent <= 60 else
                 Fraction(mantissa << (exponent - 60), 1))
        try:
            rounded = float(exact)
        except OverflowError:
            rounded = float('inf')
        if sign:
            rounded = -rounded
        expected = int.from_bytes(struct.pack('<d', rounded), 'little')
        assert pack(parts) == expected, index

    receipt = {
        'scope': 'host IEEE roundtrip/rational rounding only; native C-SKY unqualified',
        'source_sha256': {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (UNPACK, PACK)},
        'roundtrip_cases': len(roundtrips),
        'exact_rational_rounding_cases': 20000,
        'result': 'PASS',
    }
    (HERE / 'fp-pack-host-receipt.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
