#!/usr/bin/env python3
"""Bounded native RT-Thread plug_holes effects for image-B 0x100099d4."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_coalesce.c"
HERE = Path(__file__).resolve().parent
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


def put_block(buffer, offset, used, following, previous):
    struct.pack_into("<HHII", buffer, offset, 0x1ea0, used, following, previous)


def get_block(buffer, offset):
    return struct.unpack_from("<HHII", bytes(buffer), offset)


def main():
    with tempfile.TemporaryDirectory() as temporary:
        binary = Path(temporary) / "coalesce.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11",
                        str(SOURCE), "-o", str(binary)], check=True)
        function = ctypes.CDLL(str(binary)).gx8002_image_b_heap_plug_at_100099d4
        function.argtypes = [ctypes.c_void_p] * 4
        function.restype = ctypes.c_void_p
        cases = 0

        # Forward coalesce, including relocation of lowest-free pointer.
        memory = bytearray(128)
        put_block(memory, 0, 0, 32, 0)
        put_block(memory, 32, 0, 64, 0)
        put_block(memory, 64, 1, 64, 32)
        buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
        base = ctypes.addressof(buffer)
        assert function(base, base + 64, base + 32, base) == base
        assert get_block(memory, 0)[2] == 64
        assert get_block(memory, 64)[3] == 0
        cases += 1

        # Backward coalesce.
        memory = bytearray(128)
        put_block(memory, 0, 0, 32, 0)
        put_block(memory, 32, 0, 64, 0)
        put_block(memory, 64, 1, 64, 32)
        buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
        base = ctypes.addressof(buffer)
        assert function(base, base + 64, base + 32, base + 32) == base
        assert get_block(memory, 0)[2] == 64
        assert get_block(memory, 64)[3] == 0
        cases += 1

        # Both neighbors free; forward then backward order matters.
        memory = bytearray(160)
        put_block(memory, 0, 0, 32, 0)
        put_block(memory, 32, 0, 64, 0)
        put_block(memory, 64, 0, 96, 32)
        put_block(memory, 96, 1, 96, 64)
        buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
        base = ctypes.addressof(buffer)
        assert function(base, base + 96, base + 64, base + 32) == base
        assert get_block(memory, 0)[2] == 96
        assert get_block(memory, 96)[3] == 0
        cases += 1

        # Used neighbors preserve links.
        memory = bytearray(128)
        put_block(memory, 0, 1, 32, 0)
        put_block(memory, 32, 0, 64, 0)
        put_block(memory, 64, 1, 64, 32)
        before = memory.copy()
        buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
        base = ctypes.addressof(buffer)
        assert function(base, base + 64, base + 32, base + 32) == base + 32
        assert memory == before
        cases += 1

    receipt = {
        "native_entry": "0x100099d4",
        "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "upstream_source": str(UPSTREAM.relative_to(ROOT)),
        "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
        "bounded_cases": cases,
        "result": "PASS",
        "limit": "Host heap layout cases; native IRQ concurrency, allocator callers and physical SRAM unqualified.",
    }
    path = HERE / "runtime-heap-coalesce-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
