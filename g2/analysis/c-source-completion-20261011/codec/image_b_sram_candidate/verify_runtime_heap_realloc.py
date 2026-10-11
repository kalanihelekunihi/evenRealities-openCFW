#!/usr/bin/env python3
"""Bounded RT-Thread realloc split, move, failure and call effects."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
DIRECTORY = ROOT / "g2/components/gx8002/image_b_sram_candidate"
SOURCE = DIRECTORY / "backup_runtime_heap_realloc.c"
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


class State(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("end", ctypes.c_void_p),
                ("lowest_free", ctypes.c_void_p), ("aligned_size", ctypes.c_uint32),
                ("used_bytes", ctypes.c_uint32), ("maximum_used_bytes", ctypes.c_uint32)]


def prepare():
    memory = bytearray(152)
    struct.pack_into("<HHII", memory, 0, 0x1ea0, 0, 140, 0)
    struct.pack_into("<HHII", memory, 140, 0x1ea0, 1, 140, 0)
    buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
    base = ctypes.addressof(buffer)
    return memory, buffer, base, State(base, base + 140, base, 128, 0, 0)


def block(memory, offset):
    return struct.unpack_from("<HHII", memory, offset)


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text('''#include <stdint.h>
unsigned logs;
int gx8002_image_b_heap_log_10009934(const char *format, ...) {
  (void)format; ++logs; return 0;
}
int fixed_log(const char *format, uint32_t a, uint32_t b) {
  (void)a; (void)b; return gx8002_image_b_heap_log_10009934(format);
}
''')
        binary = Path(temporary) / "realloc.so"
        files = [SOURCE, DIRECTORY / "backup_runtime_heap_alloc.c",
                 DIRECTORY / "backup_runtime_heap_free.c",
                 DIRECTORY / "backup_runtime_heap_coalesce.c",
                 DIRECTORY / "backup_runtime_copy.c", stub]
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", *map(str, files), "-o", str(binary)], check=True)
        lib = ctypes.CDLL(str(binary))
        realloc = lib.gx8002_image_b_heap_realloc_at_10009ca4
        realloc.argtypes = [ctypes.POINTER(State), ctypes.c_void_p, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
        realloc.restype = ctypes.c_void_p
        logger = ctypes.cast(lib.gx8002_image_b_heap_log_10009934, ctypes.c_void_p)
        fixed = ctypes.cast(lib.fixed_log, ctypes.c_void_p)
        logs = ctypes.c_uint.in_dll(lib, "logs")
        def call(state, ptr, count):
            return realloc(ctypes.byref(state), ptr, count, logger, fixed)
        cases = 0

        memory, buffer, base, state = prepare()
        assert call(state, None, 40) == base + 12
        assert block(memory, 0) == (0x1ea0, 1, 52, 0)
        cases += 1
        assert call(state, base + 12, 40) == base + 12
        assert (state.used_bytes, state.maximum_used_bytes) == (52, 52)
        cases += 1
        assert call(state, base + 12, 12) == base + 12
        assert block(memory, 0) == (0x1ea0, 1, 24, 0)
        assert block(memory, 24) == (0x1ea0, 0, 140, 0)
        assert (state.lowest_free, state.used_bytes) == (base + 24, 24)
        cases += 1
        for i in range(12): memory[12 + i] = i + 1
        moved = call(state, base + 12, 60)
        assert moved == base + 36 and list(memory[36:48]) == list(range(1, 13))
        assert block(memory, 0)[1] == 0 and state.used_bytes == 72
        cases += 1

        # Near-fit shrink moves and copies exactly min(32, 40) bytes. Native
        # min.u32 at 0x10009d40 resolves the misleading decompiler expression.
        memory, buffer, base, state = prepare()
        assert call(state, None, 40) == base + 12
        for i in range(40): memory[12 + i] = i + 1
        moved = call(state, base + 12, 32)
        assert moved == base + 64 and list(memory[64:96]) == list(range(1, 33))
        assert block(memory, 0)[1] == 0
        cases += 1

        memory, buffer, base, state = prepare()
        assert call(state, None, 100) == base + 12
        before = memory[:]
        assert call(state, base + 12, 120) is None
        assert memory == before and state.used_bytes == 112
        cases += 1
        assert call(state, base + 140, 12) == base + 140
        cases += 1
        assert call(state, base + 12, 0) is None
        assert block(memory, 0)[1] == 0 and state.used_bytes == 0
        cases += 1
        before = memory[:]
        assert call(state, None, 129) is None and memory == before and logs.value >= 1
        cases += 1

    receipt = {"native_entry": "0x10009ca4", "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "upstream_source": str(UPSTREAM.relative_to(ROOT)), "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
               "bounded_cases": cases, "result": "PASS",
               "native_isa_proof": "0x10009d40 min.u32 r2,r4,r6 confirms min(new,old) copy count; Ghidra expression is incorrect on near-fit shrink.",
               "limit": "Host heap state and native instruction-backed branches; native IRQ concurrency and physical SRAM unqualified."}
    path = HERE / "runtime-heap-realloc-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
