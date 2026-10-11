#!/usr/bin/env python3
"""Bounded RT-Thread allocator layout and logging checks for image B."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_alloc.c"
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


class State(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("end", ctypes.c_void_p),
                ("lowest_free", ctypes.c_void_p), ("aligned_size", ctypes.c_uint32),
                ("used_bytes", ctypes.c_uint32), ("maximum_used_bytes", ctypes.c_uint32)]


LOG = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32)


def block(memory, offset):
    return struct.unpack_from("<HHII", memory, offset)


def prepare(size=128):
    memory = bytearray(size + 24)
    struct.pack_into("<HHII", memory, 0, 0x1ea0, 0, size + 12, 0)
    struct.pack_into("<HHII", memory, size + 12, 0x1ea0, 1, size + 12, 0)
    buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
    base = ctypes.addressof(buffer)
    state = State(base, base + size + 12, base, size, 0, 0)
    return memory, buffer, base, state


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text("int gx8002_image_b_heap_log_10009934(const char *s, unsigned a, unsigned b) { (void)s; (void)a; (void)b; return 0; }\n")
        binary = Path(temporary) / "alloc.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", str(SOURCE), str(stub), "-o", str(binary)], check=True)
        alloc = ctypes.CDLL(str(binary)).gx8002_image_b_heap_alloc_at_10009ab8
        alloc.argtypes = [ctypes.POINTER(State), ctypes.c_uint32, LOG]
        alloc.restype = ctypes.c_void_p
        logs = []
        @LOG
        def logger(fmt, first, second):
            logs.append((fmt.decode(), first, second))
            return 0

        cases = 0
        memory, buffer, base, state = prepare()
        before = memory[:]
        assert alloc(ctypes.byref(state), 0, logger) is None
        assert memory == before and state.used_bytes == 0 and not logs
        cases += 1

        assert alloc(ctypes.byref(state), 129, logger) is None
        assert logs == [("malloc size %d, but align to %d\n", 129, 132),
                        ("no memory\n", 0, 0)]
        assert memory == before
        cases += 1
        logs.clear()

        assert alloc(ctypes.byref(state), 17, logger) == base + 12
        assert logs == [("malloc size %d, but align to %d\n", 17, 20)]
        assert block(memory, 0) == (0x1ea0, 1, 32, 0)
        assert block(memory, 32) == (0x1ea0, 0, 140, 0)
        assert state.lowest_free == base + 32
        assert (state.used_bytes, state.maximum_used_bytes) == (32, 32)
        cases += 1
        logs.clear()

        assert alloc(ctypes.byref(state), 12, logger) == base + 44
        assert not logs
        assert block(memory, 32) == (0x1ea0, 1, 56, 0)
        assert block(memory, 56) == (0x1ea0, 0, 140, 32)
        assert (state.used_bytes, state.maximum_used_bytes) == (56, 56)
        cases += 1

        memory, buffer, base, state = prepare(40)
        assert alloc(ctypes.byref(state), 28, logger) == base + 12
        assert block(memory, 0) == (0x1ea0, 1, 52, 0)
        assert state.lowest_free == state.end == base + 52
        assert (state.used_bytes, state.maximum_used_bytes) == (52, 52)
        cases += 1

    receipt = {"native_entry": "0x10009ab8", "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "upstream_source": str(UPSTREAM.relative_to(ROOT)),
               "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
               "bounded_cases": cases, "result": "PASS",
               "limit": "Host layout/log branch checks; native IRQ concurrency and physical SRAM unqualified."}
    path = HERE / "runtime-heap-alloc-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
