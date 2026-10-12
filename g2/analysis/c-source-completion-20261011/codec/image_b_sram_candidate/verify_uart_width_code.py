#!/usr/bin/env python3
"""Native 0x10004078 input table and fallback selection, host C body check."""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / 'g2/components/gx8002/image_b_sram_candidate/backup_uart_width_code.c'
EXPECTED = {1 << shift: shift - 1 for shift in range(2, 11)}
with tempfile.TemporaryDirectory() as directory:
    library = Path(directory) / 'width.dylib'
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-dynamiclib', str(SOURCE), '-o', str(library)], check=True)
    function = ctypes.CDLL(str(library)).gx8002_image_b_uart_width_code_10004078
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                         ctypes.c_uint32]
    function.restype = ctypes.c_uint32
    cases = 0
    for mask in [0, 1, 2, *EXPECTED, 2048, 0xffffffff]:
        fallback = ctypes.c_uint32(mask)
        expected = EXPECTED.get(mask, 0)
        assert function(mask, ctypes.byref(fallback), 1) == expected
        assert function(0, ctypes.byref(fallback), 0) == expected
        cases += 2
    print(json.dumps({'native_entry': '0x10004078', 'cases': cases,
                      'result': 'PASS',
                      'limit': 'Host function body only; UART MMIO and callers unqualified.'}))
