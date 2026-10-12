#!/usr/bin/env python3
"""Pinned NationalChip CRC body against independent zlib vectors."""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_crc32.c'
with tempfile.TemporaryDirectory() as directory:
    library = Path(directory) / 'crc.dylib'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_image_b_crc32_1000c5c4
    function.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
    function.restype = ctypes.c_uint32
    cases = 0
    for size in (0, 1, 2, 3, 4, 5, 9, 32, 255):
        data = bytes((index * 37 + 11) & 255 for index in range(size))
        for alignment in range(4):
            buffer = ctypes.create_string_buffer(b'\xa5' * alignment + data + b'\0')
            address = ctypes.addressof(buffer) + alignment
            for seed in (0, 0x12345678, 0xffffffff):
                actual = function(seed, address, size)
                expected = zlib.crc32(data, seed)
                assert actual == expected, (size, alignment, seed, actual, expected)
                cases += 1
    print(json.dumps({'native_entries': ['0x1000c510', '0x1000c5c4'],
                      'cases': cases, 'result': 'PASS',
                      'limit': 'Host CRC arithmetic; target table bytes match native prefix; packet dispatch and hardware unqualified.'}))
