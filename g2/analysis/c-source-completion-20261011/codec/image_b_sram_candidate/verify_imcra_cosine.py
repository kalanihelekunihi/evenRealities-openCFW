#!/usr/bin/env python3
"""Check typed native sine table and bounded cosine interpolation inputs."""
import ctypes
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin'
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_imcra_cosine_lookup.c'
assert hashlib.sha256(IMAGE.read_bytes()).hexdigest() == \
    'd23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941'
stock = IMAGE.read_bytes()
offset = 0x100148d4 - 0x10003000
bits = [struct.unpack_from('<I', stock, offset + 4 * i)[0] for i in range(513)]
natural = [struct.unpack('<I', struct.pack('<f', math.sin(2 * math.pi * i / 512)))[0]
           for i in range(513)]
assert [i for i in range(513) if bits[i] != natural[i]] == [256, 512]
assert bits[256] == 0x2768d16e and bits[512] == 0xa7e8d16e
with tempfile.TemporaryDirectory(prefix='gx8002-imcra-cos-') as temporary:
    library = Path(temporary) / 'cosine.dylib'
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_image_b_cosine_lookup_1000ee64
    function.argtypes = [ctypes.c_float]
    function.restype = ctypes.c_float
    angles = [0.0, math.pi / 4, math.pi / 2, math.pi, 3 * math.pi / 2,
              2 * math.pi, -math.pi / 2, -math.pi]
    actual = [function(angle) for angle in angles]
    assert all(abs(value - math.cos(angle)) < 3e-5
               for angle, value in zip(angles, actual))
    print(json.dumps({'native_entry': '0x1000ee64',
                      'reconstructed_table_words': 513,
                      'stored_quarter_words': 129,
                      'formula_matched_words': 511,
                      'documented_native_zero_crossings': [256, 512],
                      'bounded_angles': len(angles), 'result': 'PASS',
                      'limit': 'Host float interpolator; C-SKY FPU rounding and exceptional inputs remain unqualified.'}))
