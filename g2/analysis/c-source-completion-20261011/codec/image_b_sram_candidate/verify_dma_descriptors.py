#!/usr/bin/env python3
"""Bounded host C descriptor words against the pinned C-SKY instruction model."""
import ctypes
import hashlib
import json
import pathlib
import random
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SOURCE_DIR = ROOT / "g2/components/gx8002/image_b_sram_candidate"
SOURCE = SOURCE_DIR / "backup_dma_descriptors.c"
OUT = HERE / "build/dma_descriptors_host.dylib"
subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-shared", "-fPIC", str(SOURCE), str(SOURCE_DIR / "backup_address_string.c"),
                "-o", str(OUT)], check=True)
lib = ctypes.CDLL(str(OUT))
fn = lib.gx8002_image_b_dma_descriptors_100048d0
fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
               ctypes.c_int32, ctypes.c_int32, ctypes.c_uint8]

def native_model(parameters, base32, count, nbytes, scale):
    # Native 0x48d0 halfword table, six-word records, signed DIVS remainder.
    config = parameters[3]
    table = (0xfff, 0xf001, 0, 0)
    src_stride = scale * table[(config >> 9) & 3]
    dst_stride = scale * table[(config >> 7) & 3]
    result = [0xa5a5a5a5] * (6 * max(count, 1))
    for i in range(max(count - 1, 0)):
        j = i * 6
        result[j] = (parameters[0] + src_stride * i) & 0xffffffff
        result[j + 1] = (parameters[1] + dst_stride * i) & 0xffffffff
        next_addr = (base32 + (j + 6) * 4) & 0xffffffff
        result[j + 2] = next_addr & 0x07ffffff if next_addr < 0x20000000 else next_addr
        result[j + 3] = config
        result[j + 4] = 0xfff
    completed = max(count - 1, 0)
    if count < 2: src_stride = dst_stride = 0
    j = completed * 6
    result[j] = (parameters[0] + src_stride * completed) & 0xffffffff
    result[j + 1] = (parameters[1] + dst_stride * completed) & 0xffffffff
    result[j + 2] = 0
    result[j + 3] = config & ~0x18000000
    quotient = abs(nbytes) // 0xfff
    if nbytes < 0: quotient = -quotient
    remainder = nbytes - quotient * 0xfff
    result[j + 4] = (remainder if remainder else 0xfff) & 0xffffffff
    return result

rng = random.Random(0x48d0)
cases = [(count, nbytes, config, scale)
         for count in (1, 2, 3, 4)
         for nbytes in (1, 4094, 4095, 4096, 8190, 8191)
         for config in (0, 0x18000000, 0x6ff, 0x3a0)
         for scale in (1, 2, 4)]
cases += [(rng.randrange(1, 9), rng.randrange(1, 32768),
           rng.getrandbits(32), rng.randrange(0, 256)) for _ in range(1024)]
for count, nbytes, config, scale in cases:
    parameters = (ctypes.c_uint32 * 4)(0x20001234, 0x20004567, 0, config)
    descriptors = (ctypes.c_uint32 * (6 * count))(*([0xa5a5a5a5] * (6 * count)))
    fn(parameters, descriptors, count, nbytes, scale)
    expected = native_model(list(parameters), ctypes.addressof(descriptors) & 0xffffffff,
                            count, nbytes, scale)
    if list(descriptors) != expected:
        raise AssertionError((count, nbytes, hex(config), scale,
                              list(descriptors), expected))
receipt = {"scope": "actual host C descriptor records vs instruction-derived native model",
           "native_entry": "100048d0", "cases": len(cases), "result": "PASS",
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "limits": "Host address truncation models 32-bit target; original C-SKY runtime and DMA hardware unqualified."}
(HERE / "dma-descriptors-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
