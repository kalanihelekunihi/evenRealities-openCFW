#!/usr/bin/env python3
"""Bounded host execution for native 0x1000b4c8 dispatch cut paths."""
import ctypes
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_audio_registration_dispatch.c'
STUBS = r'''
#include <stdint.h>
#include <string.h>
uint8_t mock_record[32];
uint32_t mock_ring_result, mock_crc_result, mock_crc_calls, mock_log_calls;
uint32_t gx8002_image_b_audio_ring_read_10009fbc(volatile int32_t *ring,
                                                   uint8_t *out) {
    (void)ring;
    if (mock_ring_result) memcpy(out, mock_record, 32);
    return mock_ring_result;
}
uint32_t gx8002_image_b_crc32_1000c5c4(uint32_t seed,
                                         const unsigned char *bytes,
                                         uint32_t length) {
    (void)bytes;
    (void)length;
    if (seed != 0) __builtin_trap();
    ++mock_crc_calls;
    return mock_crc_result;
}
int gx8002_image_b_heap_log_10009934(const char *format, ...) {
    if (strcmp(format, "Crc Error %d\n") != 0) __builtin_trap();
    ++mock_log_calls;
    return 0;
}
'''
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    stub = temporary / 'stubs.c'
    stub.write_text(STUBS)
    library = temporary / 'dispatch.dylib'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), str(stub), '-o', str(library)], check=True)
    module = ctypes.CDLL(str(library))
    function = module.gx8002_image_b_audio_registration_dispatch_at_1000b4c8
    function.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    function.restype = ctypes.c_int32
    record = (ctypes.c_ubyte * 32).in_dll(module, 'mock_record')
    table = (ctypes.c_ubyte * (16 * 28))()
    ring = (ctypes.c_int32 * 8)()
    ring_result = ctypes.c_uint32.in_dll(module, 'mock_ring_result')
    crc_result = ctypes.c_uint32.in_dll(module, 'mock_crc_result')
    crc_calls = ctypes.c_uint32.in_dll(module, 'mock_crc_calls')
    log_calls = ctypes.c_uint32.in_dll(module, 'mock_log_calls')
    cases = 0
    for available, crc_flag, actual, expected, calls, logs in (
        (0, 0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0, 0),
        (1, 1, 0x1234, 0x1234, 1, 0),
        (1, 1, 0x1234, 0x5678, 1, 1),
    ):
        ring_result.value = available
        crc_result.value = actual
        crc_calls.value = log_calls.value = 0
        record[:] = bytes(32)
        record[7] = crc_flag
        record[4:6] = struct.pack('<H', 0x55aa)
        record[0x14] = 7
        record[0x18:0x1c] = struct.pack('<I', 12)
        record[0x1c:0x20] = struct.pack('<I', expected)
        assert function(ring, table) == -1
        assert (crc_calls.value, log_calls.value) == (calls, logs)
        cases += 1
    print(json.dumps({'native_entry': '0x1000b4c8', 'cases': cases,
                      'result': 'PASS',
                      'limit': 'No-record, table-miss and CRC-failure cuts; indirect callback success and physical ring timing unqualified.'}))
