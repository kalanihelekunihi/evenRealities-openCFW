#!/usr/bin/env python3
"""Selected native heap log corpus against pinned NationalChip printf source."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_printf.c"
UPSTREAM = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/libc/printf.c"
INCLUDE = ROOT / "third-party/upstream/nationalchip-lvp-kws/include/utility/libc"
LOCAL = ROOT / "g2/components/gx8002/image_b_sram_candidate"


def main():
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        stub = temp / "stub.c"
        binary = temp / "printf.so"
        stub.write_text("""
#include <stdint.h>
char output[256]; unsigned length;
void gx8002_image_b_runtime_debug_putchar_10009990(uint32_t value) {
    if (length < sizeof(output)) output[length++] = (char)value;
}
void clear_output(void) { length = 0; }
unsigned output_length(void) { return length; }
const char *output_data(void) { return output; }
""")
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11",
                        "-I", str(INCLUDE), "-I", str(LOCAL),
                        str(SOURCE), str(stub), "-o", str(binary)], check=True)
        library = ctypes.CDLL(str(binary))
        printer = library.gx8002_image_b_heap_log_10009934
        printer.argtypes = [ctypes.c_char_p]
        printer.restype = ctypes.c_int
        library.output_length.restype = ctypes.c_uint
        library.output_data.restype = ctypes.c_void_p
        cases = [
            (b"mem init, heap begin address 0x%x, size %d\n",
             0x2001bb80, 69608,
             b"mem init, heap begin address 0x2001bb80, size 69608\n"),
            (b"mem init, error begin address 0x%x, and end address 0x%x\n",
             0x2001bb80, 0x2001bb90,
             b"mem init, error begin address 0x2001bb80, and end address 0x2001bb90\n"),
            (b"x=%08x d=%d", 0x1ea0, -12, b"x=00001ea0 d=-12"),
        ]
        for format_string, first, second, expected in cases:
            library.clear_output()
            count = printer(format_string, ctypes.c_uint32(first),
                            ctypes.c_uint32(second))
            actual = ctypes.string_at(library.output_data(), library.output_length())
            assert actual == expected, (actual, expected)
            assert count == len(expected), (count, len(expected))
    receipt = {
        "native_entries": ["0x10009934", "0x10008e20", "0x10009924"],
        "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
        "adapter_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "upstream_source": str(UPSTREAM.relative_to(ROOT)),
        "upstream_sha256": hashlib.sha256(UPSTREAM.read_bytes()).hexdigest(),
        "format_cases": len(cases),
        "result": "PASS",
        "limit": "Host output/return over heap caller formats plus one integer-format probe; full native formatting, C-SKY binary64 ABI and UART hardware unqualified.",
    }
    path = HERE / "runtime-printf-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
