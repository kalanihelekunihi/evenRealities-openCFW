#!/usr/bin/env python3
"""Bounded native-table interpreter against source parser, no device claim."""
import ctypes
import hashlib
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/uart_stage2.bin'
SOURCE = ROOT / 'g2/components/gx8002/app_callback_candidate/uart_stage2_parse_unsigned.c'
blob = IMAGE.read_bytes()
base = 0x10002800
table = blob[0x10008a88-base:0x10008a88-base+256]
assert len(table) == 256

def native_table_model(data, radix):
    pos = 0
    c = data[0]
    if c == 48:
        nxt = data[1]
        if table[nxt] & 1:
            nxt = (nxt + 32) & 255
        if nxt == 120:
            radix = 16
            pos = 2
        elif radix == 0:
            radix = 8
    elif radix == 0:
        radix = 10
    value = 0
    while True:
        c = data[pos]
        cls = table[c]
        if cls & 68:
            if cls & 1:
                c = (c + 32) & 255
            digit = c - (48 if c < 58 else 87)
            if digit >= radix:
                break
        elif radix > 256:
            digit = 256
        else:
            break
        value = (value * radix + digit) & 0xffffffff
        pos += 1
    return value, pos

with tempfile.TemporaryDirectory() as tmp:
    library = pathlib.Path(tmp) / 'parser.so'
    subprocess.run(['clang', '-std=c11', '-O2', '-shared', '-fPIC', str(SOURCE), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_uart_stage2_parse_unsigned_654c
    function.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint32]
    function.restype = ctypes.c_uint32
    cases = []
    for radix in (0, 2, 8, 10, 16, 36):
        for first in range(256):
            cases.append((bytes([first]), radix))
        for data in (b'0', b'0x', b'0XFF', b'0777', b'12345', b'FFFFFFFFF', b'aF', b' 12', b'-1', b'0xG', b'0xffjunk'):
            cases.append((data, radix))
    mismatches = []
    for data, radix in cases:
        buf = ctypes.create_string_buffer(data + b'\0\0')
        end = ctypes.c_void_p()
        result = function(ctypes.addressof(buf), ctypes.byref(end), radix)
        actual = (result, end.value - ctypes.addressof(buf))
        expected = native_table_model(data + b'\0\0', radix)
        if actual != expected:
            mismatches.append({'data': data.hex(), 'base': radix, 'expected': expected, 'actual': actual})
    receipt = {
        'image_sha256': hashlib.sha256(blob).hexdigest(),
        'native_table_sha256': hashlib.sha256(table).hexdigest(),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'cases': len(cases), 'mismatches': mismatches[:20],
        'qualification': 'native character-class table plus instruction-derived reference; host C execution, not C-SKY runtime'
    }
    target = pathlib.Path(__file__).with_name('stage2-parser-receipt.json')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'cases': len(cases), 'mismatch_count': len(mismatches), 'receipt': str(target)}))
    if mismatches:
        raise SystemExit(1)
