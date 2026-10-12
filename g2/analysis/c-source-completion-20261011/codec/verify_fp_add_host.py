#!/usr/bin/env python3
"""Host IEEE addition oracle for native soft-float parts C candidates."""
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
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate'
PATHS = [SOURCE / name for name in
         ('resident_xip_fp_parts.c', 'resident_xip_pack_double.c',
          'resident_xip_fpadd_parts.c')]

with tempfile.TemporaryDirectory() as temporary:
    binary = Path(temporary) / 'add.so'
    subprocess.run(['cc', '-std=c11', '-O2', '-shared', '-fPIC',
                    *map(str, PATHS), '-o', str(binary)], check=True)
    library = ctypes.CDLL(str(binary))
    unpack = library.gx8002_xip_unpack_double_1020a704
    unpack.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(ctypes.c_uint32)]
    add = library.gx8002_xip_fpadd_parts_10209dd8
    add.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 3
    add.restype = ctypes.POINTER(ctypes.c_uint32)
    pack = library.gx8002_xip_pack_double_1020a574
    pack.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    pack.restype = ctypes.c_uint64

    def parts(bits):
        words = (ctypes.c_uint32 * 2)(bits & 0xffffffff, bits >> 32)
        result = (ctypes.c_uint32 * 5)()
        unpack(words, result)
        return result

    rng = random.Random(0x10209dd8)
    pairs = [(0, 0), (1, 1), (1 << 63, 0),
             (0x7ff0000000000000, 0xfff0000000000000),
             (0x7fefffffffffffff, 0x7fefffffffffffff)]
    pairs += [(rng.getrandbits(64), rng.getrandbits(64))
              for _ in range(100000)]
    checked = 0
    for a, b in pairs:
        left = struct.unpack('<d', a.to_bytes(8, 'little'))[0]
        right = struct.unpack('<d', b.to_bytes(8, 'little'))[0]
        if math.isnan(left) or math.isnan(right):
            continue
        output = (ctypes.c_uint32 * 5)()
        result = add(parts(a), parts(b), output)
        expected_float = left + right
        if math.isnan(expected_float):
            continue  # Native opposite-infinity path has canonical NaN payload.
        expected = int.from_bytes(struct.pack('<d', expected_float), 'little')
        assert pack(result) == expected, (hex(a), hex(b))
        checked += 1

    receipt = {
        'scope': 'host finite/infinity IEEE arithmetic only; native C-SKY unqualified',
        'source_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(
            path.read_bytes()).hexdigest() for path in PATHS},
        'candidate_pairs': len(pairs),
        'checked_non_nan_pairs': checked,
        'result': 'PASS',
    }
    (HERE / 'fp-add-host-receipt.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
