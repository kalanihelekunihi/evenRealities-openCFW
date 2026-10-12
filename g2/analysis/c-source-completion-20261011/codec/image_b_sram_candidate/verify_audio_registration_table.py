#!/usr/bin/env python3
"""Host C record-table cases from native 0x1000b430 branch semantics."""
import ctypes
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_audio_registration_table.c'

def word(blob, index, offset=4):
    return struct.unpack_from('<I', blob, index * 28 + offset)[0]

def put(blob, index, value, offset=4):
    struct.pack_into('<I', blob, index * 28 + offset, value)

def reference(table, entry):
    key = struct.unpack_from('<I', entry, 4)[0]
    for index in range(16):
        if word(table, index) == key:
            slot = index * 28
            table[slot] = 0xff
            for offset in (4, 8, 12, 16, 24, 20):
                struct.pack_into('<I', table, slot + offset, 0)
    selected = 0
    if word(table, 0) != 0:
        selected = next((i for i in range(1, 16) if word(table, i) == 0), 16)
        if selected == 16:
            return -1
    start = selected * 28
    for offset in (4, 8, 12, 16, 24, 20):
        table[start + offset:start + offset + 4] = entry[offset:offset + 4]
    table[start] = entry[0]
    return 0

with tempfile.TemporaryDirectory() as directory:
    library = Path(directory) / 'registration.dylib'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_image_b_audio_registration_table_at_1000b430
    function.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    function.restype = ctypes.c_int32
    scenarios = [
        ([0] * 16, 0),
        ([0] * 16, 17),
        ([9] + [0] * 15, 23),
        ([1, 2, 3, 2] + [0] * 12, 2),
        (list(range(1, 17)), 99),
        ([0] * 16, 0xffffffff),
    ]
    for keys, key in scenarios:
        table = bytearray(16 * 28)
        for index, value in enumerate(keys):
            put(table, index, value)
            put(table, index, 0x12340000 + index, 8)
        entry = bytearray(28)
        entry[0] = 0x58
        put(entry, 0, key)
        for offset in (8, 12, 16, 20, 24):
            put(entry, 0, 0x20000000 + offset, offset)
        expected = bytearray(table)
        expected_status = reference(expected, entry)
        table_buffer = (ctypes.c_ubyte * len(table)).from_buffer(table)
        entry_buffer = (ctypes.c_ubyte * len(entry)).from_buffer(entry)
        assert function(table_buffer, entry_buffer) == expected_status
        assert table == expected
    print(json.dumps({'native_entry': '0x1000b430', 'cases': len(scenarios),
                      'result': 'PASS',
                      'limit': 'Host table state; final SRAM placement and concurrent ISR use unqualified.'}))
