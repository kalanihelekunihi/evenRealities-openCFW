#!/usr/bin/env python3
"""Compare the compiled EvenAI interval and pending-text accessors with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_ready_accessors_4e550a_552ce8.c"
LINKER = COMP / "even_ai_ready_accessors.ld"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ready-accessors"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
uint8_t audio_even_ai_ready_state_2006f138[0x218];
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, entry, value, handle):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_write(0x438000, payload)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x20000000, 0x100000)
    for address, blob in segments:
        uc.mem_write(address, blob)
    state = sy["audio_even_ai_ready_state_2006f138"] if compiled else 0x2006f138
    uc.mem_write(state + 8, bytes([value]))
    uc.mem_write(0x20003004, (0x20003100).to_bytes(4, "little"))
    uc.mem_write(0x20003100, b"pending\0")
    uc.reg_write(UC_ARM_REG_R0, handle)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, 0x600001)
    address = sy[entry] if compiled else {"audio_even_ai_stream_interval_get_4e550a": 0x4e550a,
                                          "audio_text_stream_pending_text_552ce8": 0x552ce8}[entry]
    uc.emu_start(address | 1, 0x600000, count=2000)
    result = uc.reg_read(UC_ARM_REG_R0)
    return (result, bytes(uc.mem_read(result, 8)).split(b"\0", 1)[0]) if entry.endswith("552ce8") \
        else result

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    if payload[0x552cf4 - 0x438000] != 0:
        raise RuntimeError("stock pending-text empty byte changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "accessor-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "accessor-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,audio_even_ai_stream_interval_get_4e550a",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    if sy["audio_text_stream_empty_552cf4"] != 0x552cf4:
        raise RuntimeError("compiled empty-string stock address changed")
    cases = 0
    for value in (0, 1, 25, 127, 255):
        name = "audio_even_ai_stream_interval_get_4e550a"
        if run(payload, segments, sy, False, name, value, 0) != \
                run(payload, segments, sy, True, name, value, 0):
            raise RuntimeError(f"EvenAI interval mismatch: {value}")
        cases += 1
    for handle in (0, 0x20003000):
        name = "audio_text_stream_pending_text_552ce8"
        stock = run(payload, segments, sy, False, name, 0, handle)
        actual = run(payload, segments, sy, True, name, 0, handle)
        if stock != actual:
            raise RuntimeError(f"EvenAI pending-text pointer mismatch: {handle:#x}: {stock!r} != {actual!r}")
        cases += 1
    receipt = {
        "status": "PASS_EXPERIMENTAL_EVEN_AI_READY_ACCESSORS_C_ORACLE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
        "oracle_elf_sha256": sha(elf_path), "cases": cases,
        "scope": "Stock return values and exact null-handle empty-string address",
        "limits": ["Final whole-image placement and all text-stream object lifetimes remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
