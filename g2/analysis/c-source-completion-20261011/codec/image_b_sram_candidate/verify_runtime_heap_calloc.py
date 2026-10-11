#!/usr/bin/env python3
"""Bounded call order and unsigned product checks for native image-B calloc."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_calloc.c"
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


def main():
    with tempfile.TemporaryDirectory() as temporary:
        stub = Path(temporary) / "stub.c"
        stub.write_text('''#include <stdint.h>
uint32_t requested, filled, value, calls;
static uint8_t memory[64];
void *gx8002_image_b_heap_alloc_10009ab8(uint32_t n) {
  requested = n; ++calls; return n && n <= sizeof(memory) ? memory : 0;
}
void gx8002_image_b_zero_100113c4(void *p, uint32_t v, uint32_t n) {
  filled = n; value = v; ++calls;
  for (uint32_t i=0;i<n;i++) ((uint8_t*)p)[i]=(uint8_t)v;
}
''')
        binary = Path(temporary) / "calloc.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11", str(SOURCE), str(stub), "-o", str(binary)], check=True)
        lib = ctypes.CDLL(str(binary))
        calloc = lib.gx8002_image_b_heap_calloc_10009c0c
        calloc.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        calloc.restype = ctypes.c_void_p
        def word(name):
            return ctypes.c_uint32.in_dll(lib, name).value
        assert calloc(3, 7) and (word("requested"), word("filled"), word("value"), word("calls")) == (21, 21, 0, 2)
        assert not calloc(10, 7) and (word("requested"), word("filled"), word("calls")) == (70, 21, 3)
        assert not calloc(0, 7) and word("requested") == 0 and word("calls") == 4
        assert calloc(0x40000000, 4) is None and word("requested") == 0 and word("calls") == 5
    receipt = {"native_entry": "0x10009c0c", "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "upstream_source": str(UPSTREAM.relative_to(ROOT)), "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
               "bounded_cases": 4, "result": "PASS", "limit": "Host call order and modulo-32-bit product; native allocator concurrency and physical SRAM unqualified."}
    path = HERE / "runtime-heap-calloc-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
