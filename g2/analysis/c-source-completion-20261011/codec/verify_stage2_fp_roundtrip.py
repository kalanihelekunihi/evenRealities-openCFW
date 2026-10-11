#!/usr/bin/env python3
"""Bounded host check of the native-derived stage2 binary64 word format.

This checks unpack/pack composition against input IEEE bit patterns. It is
not a C-SKY stock execution oracle for either standalone routine.
"""
import ctypes
import json
import random
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'g2/components/gx8002/app_callback_candidate'
with tempfile.TemporaryDirectory() as scratch:
    library = Path(scratch) / 'fp.so'
    subprocess.run(['cc', '-std=c11', '-O2', '-shared', '-fPIC',
                    str(SRC / 'uart_stage2_fp_unpack.c'),
                    str(SRC / 'uart_stage2_fp_pack.c'),
                    str(SRC / 'uart_stage2_fp_from_uint.c'),
                    str(SRC / 'uart_stage2_fp_add_internal.c'),
                    str(SRC / 'uart_stage2_fp_add_words.c'),
                    str(SRC / 'uart_stage2_fp_compare.c'),
                    str(SRC / 'uart_stage2_fp_compare_words.c'),
                    str(SRC / 'uart_stage2_fp_to_int.c'),
                    str(SRC / 'uart_stage2_fp_to_uint.c'),
                    str(SRC / 'uart_stage2_fp_mul_div.c'),
                    '-o', str(library)],
                   check=True)
    lib = ctypes.CDLL(str(library))
    u32 = ctypes.c_uint32
    pair = u32 * 2
    words = u32 * 5
    lib.gx8002_uart_stage2_fp_unpack_7d2c.argtypes = [ctypes.POINTER(u32),
                                                       ctypes.POINTER(u32)]
    lib.gx8002_uart_stage2_fp_pack_7b9c.argtypes = [ctypes.POINTER(u32)]
    lib.gx8002_uart_stage2_fp_pack_7b9c.restype = ctypes.c_uint64
    lib.gx8002_uart_stage2_fp_from_uint_7af8.argtypes = [u32]
    lib.gx8002_uart_stage2_fp_from_uint_7af8.restype = ctypes.c_uint64
    lib.gx8002_uart_stage2_fp_add_internal_7400.argtypes = [
        ctypes.POINTER(u32), ctypes.POINTER(u32), ctypes.POINTER(u32)]
    lib.gx8002_uart_stage2_fp_add_internal_7400.restype = ctypes.POINTER(u32)
    for entry in ('gx8002_uart_stage2_fp_add_words_76c4',
                  'gx8002_uart_stage2_fp_sub_words_76f4'):
        function = getattr(lib, entry)
        function.argtypes = [u32, u32, u32, u32]
        function.restype = ctypes.c_uint64
    lib.gx8002_uart_stage2_fp_to_uint_73c8.argtypes = [u32, u32]
    lib.gx8002_uart_stage2_fp_to_uint_73c8.restype = u32
    for entry in ('gx8002_uart_stage2_fp_mul_7730',
                  'gx8002_uart_stage2_fp_div_7930'):
        function = getattr(lib, entry)
        function.argtypes = [u32, u32, u32, u32]
        function.restype = ctypes.c_uint64
    rng = random.Random(0x7b9c)
    values = [0, 1, 2, (1 << 52) - 1, 1 << 52, 0x0010000000000000,
              0x7fefffffffffffff, 0x3ff0000000000000, 0x8000000000000000]
    values.extend(rng.getrandbits(64) for _ in range(10000))
    checked = 0
    mismatches = []
    for original in values:
        if (original >> 52) & 0x7ff == 0x7ff:
            continue
        internal = words()
        lib.gx8002_uart_stage2_fp_unpack_7d2c(
            pair(original & 0xffffffff, original >> 32), internal)
        restored = lib.gx8002_uart_stage2_fp_pack_7b9c(internal)
        checked += 1
        if restored != original:
            mismatches.append([hex(original), hex(restored)])
    result = {'kind': 'host source roundtrip, not stock target equality',
              'finite_cases': checked, 'mismatches': mismatches}
    integers = [0, 1, 2, 3, 0x7fffffff, 0x80000000, 0xffffffff]
    integer_rng = random.Random(0x7af8)
    integers.extend(integer_rng.getrandbits(32) for _ in range(10000))
    integer_mismatches = []
    for value in integers:
        actual = lib.gx8002_uart_stage2_fp_from_uint_7af8(value)
        expected = struct.unpack('<Q', struct.pack('<d', float(value)))[0]
        if actual != expected:
            integer_mismatches.append([hex(value), hex(actual), hex(expected)])
    result['uint32_to_binary64_cases'] = len(integers)
    result['uint32_to_binary64_mismatches'] = integer_mismatches
    add_rng = random.Random(0x7400)
    pairs = [(0x3ff0000000000000, 0x3ff0000000000000),
             (0x3ff0000000000000, 0xbff0000000000000),
             (1, 1), (0x7fefffffffffffff, 0x7fefffffffffffff)]
    pairs.extend((add_rng.getrandbits(64), add_rng.getrandbits(64))
                 for _ in range(20000))
    add_checked = 0
    add_mismatches = []
    for left_bits, right_bits in pairs:
        if ((left_bits >> 52) & 0x7ff) == 0x7ff or \
                ((right_bits >> 52) & 0x7ff) == 0x7ff:
            continue
        left = words()
        right = words()
        output = words()
        lib.gx8002_uart_stage2_fp_unpack_7d2c(
            pair(left_bits & 0xffffffff, left_bits >> 32), left)
        lib.gx8002_uart_stage2_fp_unpack_7d2c(
            pair(right_bits & 0xffffffff, right_bits >> 32), right)
        internal_result = lib.gx8002_uart_stage2_fp_add_internal_7400(
            left, right, output)
        actual = lib.gx8002_uart_stage2_fp_pack_7b9c(internal_result)
        left_float = struct.unpack('<d', struct.pack('<Q', left_bits))[0]
        right_float = struct.unpack('<d', struct.pack('<Q', right_bits))[0]
        expected = struct.unpack(
            '<Q', struct.pack('<d', left_float + right_float))[0]
        add_checked += 1
        if actual != expected:
            add_mismatches.append([hex(left_bits), hex(right_bits),
                                   hex(actual), hex(expected)])
    result['finite_add_pairs'] = add_checked
    result['finite_add_mismatches'] = add_mismatches
    wrapper_results = {}
    for entry, operation in (
            ('gx8002_uart_stage2_fp_add_words_76c4', lambda a, b: a + b),
            ('gx8002_uart_stage2_fp_sub_words_76f4', lambda a, b: a - b)):
        function = getattr(lib, entry)
        failures = []
        checked_pairs = 0
        for left_bits, right_bits in pairs:
            if ((left_bits >> 52) & 0x7ff) == 0x7ff or \
                    ((right_bits >> 52) & 0x7ff) == 0x7ff:
                continue
            left_float = struct.unpack('<d', struct.pack('<Q', left_bits))[0]
            right_float = struct.unpack('<d', struct.pack('<Q', right_bits))[0]
            expected = struct.unpack(
                '<Q', struct.pack('<d', operation(left_float, right_float)))[0]
            actual = function(left_bits & 0xffffffff, left_bits >> 32,
                              right_bits & 0xffffffff, right_bits >> 32)
            checked_pairs += 1
            if actual != expected:
                failures.append([hex(left_bits), hex(right_bits),
                                 hex(actual), hex(expected)])
        wrapper_results[entry] = {'finite_pairs': checked_pairs,
                                  'mismatches': failures}
    result['word_wrappers'] = wrapper_results
    uint_rng = random.Random(0x73c8)
    uint_values = [0, 1, 0x7fffffff, 0x80000000, 0xffffffff]
    uint_values.extend(uint_rng.getrandbits(32) for _ in range(20000))
    uint_roundtrip_failures = []
    for value in uint_values:
        binary64 = lib.gx8002_uart_stage2_fp_from_uint_7af8(value)
        restored = lib.gx8002_uart_stage2_fp_to_uint_73c8(
            binary64 & 0xffffffff, binary64 >> 32)
        if restored != value:
            uint_roundtrip_failures.append([hex(value), hex(restored)])
    result['uint32_roundtrip_cases'] = len(uint_values)
    result['uint32_roundtrip_mismatches'] = uint_roundtrip_failures
    product_rng = random.Random(0x7730)
    product_pairs = [(0x3ff0000000000000, 0x3ff0000000000000),
                     (1, 1),
                     (0x7fefffffffffffff, 0x3ff0000000000000),
                     (0, 0x3ff0000000000000)]
    product_pairs.extend((product_rng.getrandbits(64),
                          product_rng.getrandbits(64))
                         for _ in range(20000))
    arithmetic_results = {}
    for entry, operation in (
            ('gx8002_uart_stage2_fp_mul_7730', lambda a, b: a * b),
            ('gx8002_uart_stage2_fp_div_7930', lambda a, b: a / b)):
        function = getattr(lib, entry)
        failures = []
        checked_pairs = 0
        for left_bits, right_bits in product_pairs:
            if ((left_bits >> 52) & 0x7ff) == 0x7ff or \
                    ((right_bits >> 52) & 0x7ff) == 0x7ff:
                continue
            if entry.endswith('7930') and \
                    (right_bits & 0x7fffffffffffffff) == 0:
                continue
            left_float = struct.unpack('<d', struct.pack('<Q', left_bits))[0]
            right_float = struct.unpack('<d', struct.pack('<Q', right_bits))[0]
            expected = struct.unpack(
                '<Q', struct.pack('<d', operation(left_float, right_float)))[0]
            actual = function(left_bits & 0xffffffff, left_bits >> 32,
                              right_bits & 0xffffffff, right_bits >> 32)
            checked_pairs += 1
            if actual != expected:
                failures.append([hex(left_bits), hex(right_bits),
                                 hex(actual), hex(expected)])
        arithmetic_results[entry] = {'finite_pairs': checked_pairs,
                                     'mismatches': failures}
    result['mul_div_wrappers'] = arithmetic_results
    print(json.dumps(result, indent=2))
    if mismatches or integer_mismatches or add_mismatches or any(
            item['mismatches'] for item in wrapper_results.values()) or \
            uint_roundtrip_failures or any(
                item['mismatches'] for item in arithmetic_results.values()):
        raise SystemExit(1)
