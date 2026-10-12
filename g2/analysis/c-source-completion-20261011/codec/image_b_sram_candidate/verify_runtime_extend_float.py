#!/usr/bin/env python3
"""Bit compare the source binary32-to-binary64 helper for finite inputs."""
import ctypes
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_runtime_extend_float.c'
with tempfile.TemporaryDirectory(prefix='gx8002-extend-float-') as temporary:
    library = Path(temporary) / 'extend.dylib'
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), '-o', str(library)], check=True)
    function = getattr(ctypes.CDLL(str(library)), '__extendsfdf2')
    function.argtypes = [ctypes.c_float]
    function.restype = ctypes.c_double
    random_bits = random.Random(42)
    values = [0, 0x80000000, 1, 0x80000001, 0x007fffff,
              0x00800000, 0x3f800000, 0x7f7fffff]
    values += [random_bits.getrandbits(32) for _ in range(10000)]
    checked = 0
    for bits in values:
        if bits & 0x7f800000 == 0x7f800000:
            continue
        input_float = struct.unpack('<f', struct.pack('<I', bits))[0]
        actual = struct.unpack('<Q', struct.pack('<d', function(input_float)))[0]
        expected = struct.unpack('<Q', struct.pack('<d', float(input_float)))[0]
        assert actual == expected, (hex(bits), hex(actual), hex(expected))
        checked += 1
    print(json.dumps({'helper': '__extendsfdf2', 'finite_bit_patterns': checked,
                      'result': 'PASS',
                      'limit': 'Host bit comparison; signaling NaN quieting and target FP exception flags unqualified.'}))
