#!/usr/bin/env python3
"""Bounded RT-Thread heap initializer comparison for image-B 0x10009a44."""
import ctypes
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_heap_init.c"
HERE = Path(__file__).resolve().parent
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/rt_malloc/rt_mem.c"


def main():
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        stub = temp / "stub.c"
        binary = temp / "heap.so"
        stub.write_text("int gx8002_image_b_heap_log_10009934(const char *f, unsigned a, unsigned b) { (void)f; (void)a; (void)b; return 0; }\n")
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11",
                        str(SOURCE), str(stub), "-o", str(binary)], check=True)
        library = ctypes.CDLL(str(binary))
        callback_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p,
                                         ctypes.c_uint32, ctypes.c_uint32)
        initializer = library.gx8002_image_b_heap_init_at_10009a44
        initializer.argtypes = [ctypes.c_size_t, ctypes.c_size_t,
                                ctypes.POINTER(ctypes.c_uint32), callback_type]
        cases = 0
        for begin_shift, extent in ((0, 256), (1, 301), (3, 24), (0, 20)):
            heap = (ctypes.c_uint8 * 640)()
            for index in range(len(heap)):
                heap[index] = 0xa5
            control = (ctypes.c_uint32 * 6)(*[0xcccccccc] * 6)
            base = ctypes.addressof(heap)
            begin = base + 16 + begin_shift
            end = begin + extent
            logged = []

            def record(fmt, first, second):
                logged.append((fmt.decode(), first, second))
                return 0

            callback = callback_type(record)
            initializer(begin, end, control, callback)
            aligned_begin = (begin + 3) & ~3
            aligned_end = end & ~3
            if aligned_end <= 24 or aligned_end - 24 < aligned_begin:
                assert list(control) == [0xcccccccc] * 6
                assert logged == [("mem init, error begin address 0x%x, and end address 0x%x\n",
                                   begin & 0xffffffff, end & 0xffffffff)]
            else:
                size = aligned_end - aligned_begin - 24
                tail_offset = size + 12
                actual = bytes(heap)
                first_offset = aligned_begin - base
                last_offset = first_offset + tail_offset
                assert struct.unpack_from("<HHII", actual, first_offset) == (
                    0x1ea0, 0, tail_offset, 0)
                assert struct.unpack_from("<HHII", actual, last_offset) == (
                    0x1ea0, 1, tail_offset, tail_offset)
                assert list(control) == [aligned_begin & 0xffffffff,
                                         (aligned_begin + tail_offset) & 0xffffffff,
                                         aligned_begin & 0xffffffff, size,
                                         0xcccccccc, 0xcccccccc]
                assert logged == [("mem init, heap begin address 0x%x, size %d\n",
                                   aligned_begin & 0xffffffff, size)]
            cases += 1
    receipt = {
        "native_entries": ["0x10009a44", "0x10009f10"],
        "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "upstream_source": str(UPSTREAM.relative_to(ROOT)),
        "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
        "bounded_layout_cases": cases,
        "result": "PASS",
        "limit": "Host pointer relocation checks selected success/error fields; native formatter output and physical heap allocation remain external contracts.",
    }
    path = HERE / "runtime-heap-init-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
