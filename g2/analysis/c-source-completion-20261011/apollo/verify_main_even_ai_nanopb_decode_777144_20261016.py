#!/usr/bin/env python3
"""Compare pinned nanopb C + recovered descriptor with stock EvenAI decode."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
UPSTREAM = ROOT / "third-party/upstream/nanopb"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
DESC = G2 / "components/audio/uart_thread_source_candidate/even_ai_descriptor_777144.c"
CONTEXT = G2 / "components/audio/uart_thread_source_candidate/even_ai_decoder_context_48f49c.c"
ARCHIVE = G2 / "build/c-firmware/20261016/main-nanopb-pinned/libg2_nanopb.a"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"],
                               text=True).strip() == "98bf4db69897b53434f3d0ba72e0a3ab1a902824"

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    libc = temp / "libc.c"
    libc.write_text("""#include <stddef.h>
void *memcpy(void *d,const void *s,size_t n){unsigned char *a=d;const unsigned char *b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}
void *memset(void *d,int c,size_t n){unsigned char *a=d;for(size_t i=0;i<n;i++)a[i]=(unsigned char)c;return d;}
""")
    elf = temp / "nanopb.elf"
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
             '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
             "-I", str(CONFIG), "-I", str(UPSTREAM)]
    subprocess.run(["clang", *flags, "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,pb_decode", str(DESC), str(CONTEXT), str(libc),
                    str(ARCHIVE), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, wire):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.mem_write(0x20001000, wire + b"\xa5" * (128 - len(wire)))
        cpu.mem_write(0x20000300, b"\x00" * 0x20c)
        reader = ((symbols["audio_even_ai_decoder_read_48f3a4"] | 1)
                  if compiled else 0x48f3a5)
        context = (reader.to_bytes(4, "little") + (0x20001000).to_bytes(4, "little") +
                   len(wire).to_bytes(4, "little") + b"\x00" * 4)
        cpu.mem_write(0x20000200, context)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20000200)
        cpu.reg_write(A.UC_ARM_REG_R1,
                      symbols["audio_even_ai_decode_fields"] if compiled else 0x777144)
        cpu.reg_write(A.UC_ARM_REG_R2, 0x20000300)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cpu.emu_start((symbols["pb_decode"] if compiled else 0x490120) | 1,
                      0x600000, count=500000)
        state = bytes(cpu.mem_read(0x20000200, 16))
        return (cpu.reg_read(A.UC_ARM_REG_R0) & 0xff,
                state[4:12], bytes(cpu.mem_read(0x20000300, 0x20c)))

    wires = [b"", b"\x08\x01", b"\x10\x02", b"\x08\x01\x10\x02",
             b"\x1a\x00", b"\x22\x00", b"\x08", b"\xff", b"\x78\x01",
             b"\x08\x80\x01", b"\x08\x01\x1a\x00"]
    for tag in range(3, 14):
        field = bytes([(tag << 3) | 2])
        wires.append(field + b"\x00")
        wires.append(b"\x08\x01\x10\x02" + field + b"\x02\x08\x01")
    returns = []
    for wire in wires:
        stock, source = run(False, wire), run(True, wire)
        assert stock == source, (wire.hex(), stock[:2], source[:2],
                                 stock[2][:32].hex(), source[2][:32].hex())
        returns.append(stock[0])
    assert 0 in returns and 1 in returns, returns

    output = G2 / "build/c-firmware/20261016/main-even-ai-nanopb-decode-777144/oracle-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_NATIVE_MAIN_EVEN_AI_NANOPB_DECODE_777144",
               "cases": len(wires),
               "inputs_hex": [x.hex() for x in wires],
               "returns": returns,
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "descriptor_source": str(DESC.relative_to(ROOT)),
               "descriptor_source_sha256": hashlib.sha256(DESC.read_bytes()).hexdigest(),
               "nanopb_archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
               "limits": "decoder return, cursor, remaining bytes, and 0x20c output only; no frame command handlers"}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(wires), hashlib.sha256(output.read_bytes()).hexdigest())
