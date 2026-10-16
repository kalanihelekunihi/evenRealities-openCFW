#!/usr/bin/env python3
"""Controlled stock/compiled oracle for Apollo file-heap realloc wrapper."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/file_heap_realloc_474d54.c"
OUT = G2 / "build/c-firmware/20261016/main-file-heap-realloc"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void *g2_codec_heap_mutex;
void *g2_codec_heap_pool;
int32_t audio_file_mutex_acquire(void*p,uint32_t t){(void)p;(void)t;return 0;}
int32_t audio_file_mutex_release(void*p){(void)p;return 0;}
void *g2_tlsf_reallocate_4d0868(void*p,void*q,uint32_t n){(void)p;(void)q;(void)n;return 0;}
void g2_file_heap_error_log(const char*p){(void)p;}
void g2_file_close_error(const char*a,const char*b,uint32_t c){(void)a;(void)b;(void)c;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, old, size, lock_result, realloc_result):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    mutex_cell = sy["g2_codec_heap_mutex"] if compiled else 0x200748f8
    pool_cell = sy["g2_codec_heap_pool"] if compiled else 0x20074abc
    cpu.mem_write(mutex_cell, (0x20003000).to_bytes(4, "little"))
    cpu.mem_write(pool_cell, (0x20004000).to_bytes(4, "little"))
    cpu.reg_write(UC_ARM_REG_R0, old)
    cpu.reg_write(UC_ARM_REG_R1, size)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_file_mutex_acquire": "lock", "g2_tlsf_reallocate_4d0868": "realloc",
             "audio_file_mutex_release": "unlock", "g2_file_heap_error_log": "error",
             "g2_file_close_error": "close"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x4497b6: "lock", 0x4d0868: "realloc", 0x44981c: "unlock",
              0x4733ee: "error", 0x4d09b4: "close"})
    calls = []
    def intercept(machine, pc, width, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        r1 = machine.reg_read(UC_ARM_REG_R1)
        r2 = machine.reg_read(UC_ARM_REG_R2)
        calls.append((kind, r0, r1, r2) if kind in ("realloc", "close") else
                     (kind, r0, r1) if kind == "lock" else (kind, r0))
        machine.reg_write(UC_ARM_REG_R0, lock_result if kind == "lock" else
                          realloc_result if kind == "realloc" else 0)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_file_heap_realloc"] if compiled else 0x474d54
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return cpu.reg_read(UC_ARM_REG_R0), calls

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "heap-realloc-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "heap-realloc-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_file_heap_realloc",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for old in (0, 0x20005000):
        for size in (0, 0x200):
            for lock_result in (0, 1):
                for realloc_result in (0, 0x20006000):
                    stock = run(payload, segments, sy, False, old, size, lock_result, realloc_result)
                    actual = run(payload, segments, sy, True, old, size, lock_result, realloc_result)
                    if stock != actual:
                        raise RuntimeError(f"heap realloc mismatch {(old, size, lock_result, realloc_result)}: {stock!r} != {actual!r}")
                    cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_FILE_HEAP_REALLOC_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Mutex, TLSF, error callbacks and return across controlled cases",
               "limits": ["TLSF and mutex internals, error reporting side effects, RAM ownership remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
