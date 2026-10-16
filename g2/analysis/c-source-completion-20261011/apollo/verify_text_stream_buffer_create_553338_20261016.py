#!/usr/bin/env python3
"""Controlled stock/compiled oracle for text-stream ensure_text_capacity."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_buffer_create_553338.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-buffer-create"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void *audio_file_heap_realloc(void*p,uint32_t n){(void)p;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, owner, capacity, required, succeed, mode):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    cpu.mem_write(0x20001000, (0x20003000).to_bytes(4, "little"))
    cpu.mem_write(0x20001004, capacity.to_bytes(4, "little"))
    cpu.reg_write(UC_ARM_REG_R0, 0x20002000 if owner else 0)
    cpu.reg_write(UC_ARM_REG_R1, 0x20001000)
    cpu.reg_write(UC_ARM_REG_R2, 0x20001004)
    cpu.reg_write(UC_ARM_REG_R3, required)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_file_heap_realloc": "realloc", "audio_log_flags": "flag",
             "audio_log_extended": "extended", "compressed_log_output": "compressed"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x474d54: "realloc", 0x43d0ce: "flag", 0x43d574: "extended",
              0x43ce9e: "compressed"})
    calls = []
    def cstring(p):
        return bytes(cpu.mem_read(p, 240)).split(b"\0", 1)[0].decode("ascii")
    def intercept(machine, pc, size, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        if kind == "realloc":
            calls.append((kind, r0, machine.reg_read(UC_ARM_REG_R1)))
            result = 0x20004000 if succeed else 0
        elif kind == "extended":
            sp = machine.reg_read(UC_ARM_REG_SP)
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2)),
                          cstring(machine.reg_read(UC_ARM_REG_R3)),
                          int.from_bytes(machine.mem_read(sp, 4), "little"),
                          cstring(int.from_bytes(machine.mem_read(sp + 4, 4), "little"))))
            result = 0
        elif kind == "compressed":
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2))))
            result = 0
        else:
            calls.append((kind,))
            result = mode
        machine.reg_write(UC_ARM_REG_R0, result)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_text_stream_buffer_create_553338"] if compiled else 0x553338
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return cpu.reg_read(UC_ARM_REG_R0), bytes(cpu.mem_read(0x20001000, 8)), calls

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "buffer-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "buffer-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_buffer_create_553338",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for owner in (0, 1):
        for capacity, required in ((0, 0x200), (0x80, 0x200), (0x100, 0x200),
                                   (0x200, 0x200), (0x300, 0x100)):
            for succeed in (False, True):
                for mode in (0, 1, 2, 4, 7):
                    stock = run(payload, segments, sy, False, owner, capacity, required, succeed, mode)
                    actual = run(payload, segments, sy, True, owner, capacity, required, succeed, mode)
                    if stock != actual:
                        raise RuntimeError(f"buffer mismatch {(owner, capacity, required, succeed, mode)}: {stock!r} != {actual!r}")
                    cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_BUFFER_CREATE_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Capacity decisions, reallocator arguments, buffer cells and error logging",
               "limits": ["Heap reallocator and logger effects remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
