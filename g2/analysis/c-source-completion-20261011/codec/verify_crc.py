#!/usr/bin/env python3
"""Pinned CRC table identity and host C/zlib arithmetic; not stock execution."""
import ctypes
import hashlib
import json
from pathlib import Path
import random
import re
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261011/codec-crc-arithmetic"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "third-party/upstream/nationalchip-lvp-kws/base/src/crc32.c"
PORT = ROOT / "g2/components/gx8002/app_callback_candidate/crc_port"
IMAGE = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin"
RUN = ROOT / "g2/research/corpus/codec/ghidra/open-2026-09-29/image_a_xip/RUN.json"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(IMAGE) == json.loads(RUN.read_text())["image_sha256"]
table_text = SOURCE.read_text().split("local const uint32_t crc_table[256] = {", 1)[1].split("};", 1)[0]
values = [int(value, 16) for value in re.findall(r"tole\(0x([0-9a-fA-F]+)L\)", table_text)]
assert len(values) == 256
table = struct.pack("<256I", *values)
offset = 0x1020b908 - 0x10203004
assert IMAGE.read_bytes()[offset:offset + 1024] == table
library = OUT / "crc.dylib"
subprocess.run(["clang", "-std=c11", "-O2", "-shared", "-fPIC", "-I" + str(PORT), str(SOURCE), "-o", str(library)], check=True)
crc = ctypes.CDLL(str(library)).crc32
crc.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
crc.restype = ctypes.c_uint32
rng = random.Random(0x102098a8)
cases = 0
for alignment in range(4):
    for size in list(range(65)) + [127, 128, 255, 256, 511, 512, 1023, 1024]:
        data = rng.randbytes(size)
        storage = ctypes.create_string_buffer(size + 32)
        address = ctypes.addressof(storage) + 8 + alignment
        ctypes.memmove(address, data, size)
        for seed in [0, 1, 0xffffffff, 0x80000000, rng.getrandbits(32)]:
            assert crc(seed, address, size) == zlib.crc32(data, seed), (alignment, size, seed)
            cases += 1
receipt = {"source_sha256": sha(SOURCE), "port_sha256": sha(PORT / "common.h"),
           "image_sha256": sha(IMAGE), "table_address": "0x1020b908", "table_words_verified": 256,
           "table_sha256": hashlib.sha256(table).hexdigest(), "host_shared_library_sha256": sha(library),
           "host_c_zlib_cases": cases, "result": "pass", "original_instruction_execution": False,
           "producing_compiler_identity": False}
Path(__file__).with_name("crc-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"host_c_zlib_cases": cases, "table_words_verified": 256, "result": "pass"}))
