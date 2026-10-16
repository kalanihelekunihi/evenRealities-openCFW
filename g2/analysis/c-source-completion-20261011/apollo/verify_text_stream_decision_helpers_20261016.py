#!/usr/bin/env python3
"""Controlled stock/C oracle for text-stream validation and next interval."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_decision_helpers_5533cc_5532f8.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-decision-helpers"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
int32_t audio_uart_font_path_compare(const char*a,const char*b){(void)a;(void)b;return 0;}
uint32_t strlen(const char*a){(void)a;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def machine(payload, segments):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    return cpu

def run_validate(payload, segments, sy, compiled, present, mode, compare_result, length):
    cpu = machine(payload, segments)
    obj = 0x20003000
    cpu.mem_write(obj, (0x20004000).to_bytes(4, "little"))
    cpu.mem_write(0x20004000, b"old\0")
    cpu.mem_write(0x20005000, b"new\0")
    cpu.reg_write(UC_ARM_REG_R0, obj if present else 0)
    cpu.reg_write(UC_ARM_REG_R1, 0x20005000)
    cpu.reg_write(UC_ARM_REG_R2, mode)
    hooks = ({sy["audio_uart_font_path_compare"] & ~1: "compare",
              sy["strlen"] & ~1: "length"} if compiled else
             {0x46cacc: "compare", 0x44a43c: "length"})
    calls = []
    def intercept(m, pc, width, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        calls.append((kind, m.reg_read(UC_ARM_REG_R0), m.reg_read(UC_ARM_REG_R1))
                     if kind == "compare" else (kind, m.reg_read(UC_ARM_REG_R0)))
        m.reg_write(UC_ARM_REG_R0, compare_result if kind == "compare" else length)
        m.reg_write(UC_ARM_REG_PC, m.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_text_stream_validate_5533cc"] if compiled else 0x5533cc
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return cpu.reg_read(UC_ARM_REG_R0), calls

def run_interval(payload, segments, sy, compiled, present, second, total, copied,
                 interval, multiply_flag):
    cpu = machine(payload, segments)
    obj = 0x20003000
    seed = bytearray(0x30)
    for off, value in ((4, 0x20004000 if second else 0), (8, interval),
                       (0x0c, copied), (0x10, total)):
        seed[off:off+4] = value.to_bytes(4, "little")
    seed[0x2c] = multiply_flag
    cpu.mem_write(obj, bytes(seed))
    cpu.reg_write(UC_ARM_REG_R0, obj if present else 0)
    entry = sy["audio_text_stream_next_interval_5532f8"] if compiled else 0x5532f8
    cpu.emu_start(entry | 1, 0x600000, count=1000)
    return cpu.reg_read(UC_ARM_REG_R0)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "decision-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "decision-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_validate_5533cc",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for present in (False, True):
        for mode in (0, 1, 2, 3, 0x101):
            for comparison in (0, 1):
                for length in (0, 3):
                    args = (present, mode, comparison, length)
                    stock = run_validate(payload, segments, sy, False, *args)
                    actual = run_validate(payload, segments, sy, True, *args)
                    if stock != actual:
                        raise RuntimeError(f"validation mismatch {args}: {stock!r} != {actual!r}")
                    cases += 1
    for present in (False, True):
        for second in (False, True):
            for total, copied in ((0, 0), (5, 0), (5, 4), (5, 5), (0, 0xffffffff)):
                for interval in (0, 25):
                    for flag in (0, 1):
                        args = (present, second, total, copied, interval, flag)
                        stock = run_interval(payload, segments, sy, False, *args)
                        actual = run_interval(payload, segments, sy, True, *args)
                        if stock != actual:
                            raise RuntimeError(f"interval mismatch {args}: {stock!r} != {actual!r}")
                        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_DECISION_HELPERS_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Mode validation and signed interval arithmetic",
               "limits": ["String helper internals and malformed pointers remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
