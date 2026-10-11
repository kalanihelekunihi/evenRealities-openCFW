#!/usr/bin/env python3
"""Compare actual host C write traces with an ISA-derived native loop model."""
import ctypes
import hashlib
import json
import pathlib
import random
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_dcache_range.c"
BRIDGE = HERE / "cache_trace_bridge.c"
OUT = HERE / "build/cache_trace_host.dylib"
OUT.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-shared", "-fPIC", "-DGX8002_IMAGE_B_CACHE_TRACE",
                str(SOURCE), str(BRIDGE), "-o", str(OUT)], check=True)
lib = ctypes.CDLL(str(OUT))
lib.gx8002_cache_trace_at.argtypes = [ctypes.c_uint32]
lib.gx8002_cache_trace_at.restype = ctypes.c_uint32
lib.gx8002_cache_trace_count.restype = ctypes.c_uint32
for name in ("gx8002_image_b_dcache_invalidate_range_10004dd8",
             "gx8002_image_b_dcache_clean_range_10004e74",
             "gx8002_image_b_dcache_clean_invalidate_range_10004f10"):
    getattr(lib, name).argtypes = [ctypes.c_uint32, ctypes.c_int32]

MASK = 0xffffffff
def native_instruction_model(address, length, command):
    # 0x4dd8/0x4e74: AND ~15, OR command, signed compare with 128.
    r0 = ((address & ~15) | command) & MASK
    r1 = length
    writes = []
    if r1 >= 128:
        r1 -= 128
        r18 = r1 & ~127
        r13 = (r0 + r18 + 128) & MASK
        r3 = r0
        while True:
            for offset in (0, 16, 32, 48, 64, 80, 96, 112):
                writes.append((r3 + offset) & MASK)
            r3 = (r3 + 128) & MASK
            if r3 == r13: break
        r0 = (r0 + (r1 & ~127) + 128) & MASK
        r1 -= r18
    if r1 > 0:
        r2 = (r0 + 16 + ((r1 - 1) & ~15)) & MASK
        r3 = (r0 + 16) & MASK
        while True:
            writes.append(r0)
            r0 = r3
            if r3 == r2: break
            r3 = (r3 + 16) & MASK
    return writes

cases = [(address, length) for address in (0, 1, 15, 16, 0x10004003,
                                           0xfffffff0, 0xfffffff7)
         for length in (-1, 0, 1, 15, 16, 17, 127, 128, 129, 143, 144,
                        255, 256, 257, 511, 512, 1025)]
rng = random.Random(0x4e74)
cases += [(rng.getrandbits(32), rng.randrange(0, 4097)) for _ in range(2048)]
for address, length in cases:
    for command, name in ((2, "gx8002_image_b_dcache_invalidate_range_10004dd8"),
                          (8, "gx8002_image_b_dcache_clean_range_10004e74"),
                          (10, "gx8002_image_b_dcache_clean_invalidate_range_10004f10")):
        lib.gx8002_cache_trace_reset()
        getattr(lib, name)(address, length)
        got = [lib.gx8002_cache_trace_at(i) for i in range(lib.gx8002_cache_trace_count())]
        expected = native_instruction_model(address, length, command)
        if got != expected:
            raise AssertionError((hex(address), length, command, got[:24], expected[:24]))
receipt = {"scope": "actual host C write traces vs ISA-derived native loop model",
           "native_entries": ["10004dd8", "10004e74", "10004f10"],
           "case_pairs": len(cases), "trace_comparisons": len(cases) * 3,
           "result": "PASS", "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "limits": "Native instructions modeled from pinned disassembly; no original C-SKY execution or cache hardware qualification."}
(HERE / "cache-range-trace-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
