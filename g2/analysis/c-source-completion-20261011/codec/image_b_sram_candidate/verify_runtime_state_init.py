#!/usr/bin/env python3
"""Bounded native descriptor layout comparison for image-B 0x10009d7c."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_state_init.c"
HERE = Path(__file__).resolve().parent
FIELDS = [
    (0x00, 0x20191222), (0x08, 2), (0x50, 0x20030000),
    (0x54, 12288), (0x18, 1), (0x48, 0x2001a380),
    (0x4c, 6144), (0x34, 12), (0x28, 12), (0x6c, 40),
    (0x60, 256), (0x1c, 16), (0x44, 2784), (0x20, 16000),
    (0x40, 2816), (0x0c, 0), (0x58, 0), (0x5c, 0),
    (0x10, 0), (0x64, 0), (0x68, 0), (0x2c, 0), (0x14, 0),
    (0x70, 0), (0x74, 0), (0x30, 0), (0x24, 3),
    (0x38, "ring"), (0x3c, 4), (0x04, 0),
]


def main():
    fixture = r'''
#include <stdint.h>
#include <string.h>
uintptr_t calls[2]; uint32_t sizes[2]; int count;
void gx8002_image_b_zero_100113c4(void *p,uint32_t v,uint32_t n) {
    if (count < 2) { calls[count]=(uintptr_t)p; sizes[count]=n; }
    ++count; memset(p,(unsigned char)v,n);
}
int get_count(void) { return count; }
uintptr_t get_call(int i) { return calls[i]; }
uint32_t get_size(int i) { return sizes[i]; }
void reset_calls(void) { count=0; }
'''
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        stub = temp / "stub.c"
        binary = temp / "state.so"
        stub.write_text(fixture)
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11",
                        str(SOURCE), str(stub), "-o", str(binary)], check=True)
        library = ctypes.CDLL(str(binary))
        init = library.gx8002_image_b_runtime_state_init_at_10009d7c
        init.argtypes = [ctypes.c_size_t]
        library.get_call.argtypes = [ctypes.c_int]
        library.get_call.restype = ctypes.c_size_t
        library.get_size.argtypes = [ctypes.c_int]
        cases = 0
        for seed in (0x11, 0x5a, 0xff):
            buffer = (ctypes.c_uint8 * 11408)()
            for index in range(len(buffer)):
                buffer[index] = (seed + index * 13) & 255
            base = ctypes.addressof(buffer)
            expected = bytearray(buffer)
            expected[:120] = bytes(120)
            expected[128:128 + 11264] = bytes(11264)
            for offset, value in FIELDS:
                if value == "ring":
                    value = (base + 128) & 0xffffffff
                struct.pack_into("<I", expected, offset, value)
            library.reset_calls()
            init(base)
            assert bytearray(buffer) == expected
            assert library.get_count() == 2
            assert [library.get_call(i) for i in (0, 1)] == [base, base + 128]
            assert [library.get_size(i) for i in (0, 1)] == [120, 11264]
            cases += 1
    receipt = {
        "native_entry": "0x10009d7c",
        "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "bounded_layout_cases": cases,
        "field_writes": len(FIELDS),
        "native_clear_lengths": [120, 11264],
        "native_clear_second_offset": 128,
        "result": "PASS",
        "limit": "Host relocated backing array and stubbed native fill-call effects; actual SRAM availability, state consumers and final placement unqualified.",
    }
    path = HERE / "runtime-state-init-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
