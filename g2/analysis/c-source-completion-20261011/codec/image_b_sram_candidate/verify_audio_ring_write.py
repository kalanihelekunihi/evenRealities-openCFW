#!/usr/bin/env python3
"""Bounded native 0x10015b64 ring-writer state transitions."""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_audio_ring.c'
STUBS = '''
#include <stdint.h>
uint32_t gx8002_image_b_audio_state_word_50_10009e18(void){return 0;}
uint32_t gx8002_image_b_audio_state_word_54_10009e24(void){return 0;}
uint32_t gx8002_image_b_audio_state_word_70_10009e30(void){return 0;}
uint32_t gx8002_image_b_audio_state_word_74_10009e3c(void){return 0;}
uint32_t gx8002_image_b_audio_word_08_10009f9c(void){return 1;}
'''
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    stub = temporary / 'stubs.c'
    stub.write_text(STUBS)
    library = temporary / 'ring.dylib'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), str(stub), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_image_b_audio_ring_write_at_10015b64
    function.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_void_p, ctypes.c_void_p]
    function.restype = ctypes.c_uint32
    scenarios = [
        (0, 4, 4, 8, 0),
        (0, 5, 3, 8, 1),
        (6, 4, 3, 8, 1),
        (6, 1, 3, 8, 0),
        (6, 4, 0, 8, 1),
        (2, 5, -1, 8, 1),
    ]
    for write, read, count, capacity, result in scenarios:
        ring = (ctypes.c_int32 * 5)(write, read, 0, capacity, count)
        output = (ctypes.c_ubyte * capacity)(*([0xaa] * capacity))
        payload = (ctypes.c_ubyte * 8)(1, 2, 3, 4, 5, 6, 7, 8)
        before = bytes(output)
        actual = function(ring, output, payload)
        assert actual == result
        next_index = (write + count) % capacity
        if result == 0:
            assert ring[0] == write and bytes(output) == before
        else:
            assert ring[0] == next_index
            expected = bytearray(before)
            for index in range(max(0, count)):
                expected[(write + index) % capacity] = payload[index]
            assert bytes(output) == bytes(expected)
    print(json.dumps({'native_entry': '0x10015b64', 'cases': len(scenarios),
                      'result': 'PASS',
                      'limit': 'Host ring state; SRAM placement, concurrent ISR, and invalid capacity unqualified.'}))
