#!/usr/bin/env python3
"""Bounded free and coalescing effects for native image-B 0x10009c2c."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_free.c"
COALESCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_coalesce.c"
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


class State(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("end", ctypes.c_void_p),
                ("lowest_free", ctypes.c_void_p), ("aligned_size", ctypes.c_uint32),
                ("used_bytes", ctypes.c_uint32), ("maximum_used_bytes", ctypes.c_uint32)]


def prepare():
    memory = bytearray(152)
    struct.pack_into("<HHII", memory, 0, 0x1ea0, 1, 32, 0)
    struct.pack_into("<HHII", memory, 32, 0x1ea0, 0, 140, 0)
    struct.pack_into("<HHII", memory, 140, 0x1ea0, 1, 140, 32)
    buffer = (ctypes.c_uint8 * len(memory)).from_buffer(memory)
    base = ctypes.addressof(buffer)
    return memory, buffer, base, State(base, base + 140, base + 32, 128, 32, 32)


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text('''#include <stdarg.h>
unsigned logs;
int gx8002_image_b_heap_log_10009934(const char *format, ...) {
  (void)format; ++logs; return 0;
}
''')
        binary = Path(temporary) / "free.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", str(SOURCE), str(COALESCE), str(stub), "-o", str(binary)], check=True)
        lib = ctypes.CDLL(str(binary))
        free = lib.gx8002_image_b_heap_free_at_10009c2c
        free.argtypes = [ctypes.POINTER(State), ctypes.c_void_p, ctypes.c_void_p]
        free.restype = None
        logger = ctypes.cast(lib.gx8002_image_b_heap_log_10009934, ctypes.c_void_p)
        logs = ctypes.c_uint.in_dll(lib, "logs")
        cases = 0

        memory, buffer, base, state = prepare()
        before = memory[:]
        free(ctypes.byref(state), None, logger)
        assert memory == before and state.used_bytes == 32 and logs.value == 0
        cases += 1

        free(ctypes.byref(state), base + 140, logger)
        assert memory == before and state.used_bytes == 32 and logs.value == 1
        cases += 1

        free(ctypes.byref(state), base + 12, logger)
        assert struct.unpack_from("<HHII", memory, 0) == (0x1ea0, 0, 140, 0)
        assert struct.unpack_from("<HHII", memory, 140)[3] == 0
        assert state.lowest_free == base and state.used_bytes == 0
        cases += 1

        # Free the second used block and merge it backward into free block 0.
        memory, buffer, base, state = prepare()
        struct.pack_into("<HHII", memory, 0, 0x1ea0, 0, 32, 0)
        struct.pack_into("<HHII", memory, 32, 0x1ea0, 1, 140, 0)
        state.lowest_free = base
        state.used_bytes = 108
        free(ctypes.byref(state), base + 44, logger)
        assert struct.unpack_from("<HHII", memory, 0) == (0x1ea0, 0, 140, 0)
        assert state.lowest_free == base and state.used_bytes == 0
        cases += 1

        # Native logs a bad-header diagnostic but still performs the free.
        memory, buffer, base, state = prepare()
        struct.pack_into("<HH", memory, 0, 0, 0)
        logged_before = logs.value
        free(ctypes.byref(state), base + 12, logger)
        assert logs.value == logged_before + 2
        assert struct.unpack_from("<HHII", memory, 0) == (0x1ea0, 0, 140, 0)
        assert state.used_bytes == 0
        cases += 1

    receipt = {"native_entry": "0x10009c2c", "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "upstream_source": str(UPSTREAM.relative_to(ROOT)), "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
               "bounded_cases": cases, "result": "PASS", "limit": "Host heap structure and branch effects; invalid-header diagnostic argument formatting, IRQ concurrency, and physical SRAM unqualified."}
    path = HERE / "runtime-heap-free-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
