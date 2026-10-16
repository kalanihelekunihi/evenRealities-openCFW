#!/usr/bin/env python3
"""Compare text-stream allocator object and cleanup against pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_create_552b30.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-create"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void *codec_allocate(uint32_t n){(void)n;return 0;}
void audio_file_heap_free(void *p){(void)p;}
uint32_t audio_even_ai_mutex_create_44971c(const void *p){(void)p;return 0;}
void audio_uart_mutex_delete(uint32_t x){(void)x;}
uint32_t audio_text_stream_buffer_create_553338(void*a,void*b,void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, fail):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    obj = 0x20001000
    cpu.mem_write(obj, bytes([0xa5]) * 0x30)
    cpu.mem_write(0x20002000, b"X")
    cpu.mem_write(0x20003000, b"Y")
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"codec_allocate": "alloc", "audio_file_heap_free": "free",
             "audio_even_ai_mutex_create_44971c": "mutex", "audio_uart_mutex_delete": "delete",
             "audio_text_stream_buffer_create_553338": "buffer"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x474cd2: "alloc", 0x474d16: "free", 0x44971c: "mutex",
              0x44986e: "delete", 0x553338: "buffer"})
    calls = []
    buffer_count = 0
    def intercept(machine, pc, size, unused):
        nonlocal buffer_count
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        if kind == "buffer":
            buffer_count += 1
            r1 = machine.reg_read(UC_ARM_REG_R1)
            r2 = machine.reg_read(UC_ARM_REG_R2)
            r3 = machine.reg_read(UC_ARM_REG_R3)
            calls.append((kind, r0, r1, r2, r3))
            if fail != f"buffer{buffer_count}":
                machine.mem_write(r1, (0x20001000 + buffer_count * 0x1000).to_bytes(4, "little"))
                machine.mem_write(r2, (0x200).to_bytes(4, "little"))
            result = 0 if fail == f"buffer{buffer_count}" else 1
        else:
            calls.append((kind, r0))
            result = (0 if fail == "alloc" else obj) if kind == "alloc" else \
                (0 if fail == "mutex" else 0x20004000) if kind == "mutex" else 0
        machine.reg_write(UC_ARM_REG_R0, result)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_text_stream_create_552b30"] if compiled else 0x552b30
    cpu.emu_start(entry | 1, 0x600000, count=3000)
    return (cpu.reg_read(UC_ARM_REG_R0), bytes(cpu.mem_read(obj, 0x30)),
            bytes(cpu.mem_read(0x20002000, 1)), bytes(cpu.mem_read(0x20003000, 1)), calls)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "allocator-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "allocator-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_create_552b30",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for fail in ("alloc", "mutex", "buffer1", "buffer2", "none"):
        stock = run(payload, segments, sy, False, fail)
        actual = run(payload, segments, sy, True, fail)
        if stock != actual:
            raise RuntimeError(f"allocator mismatch {fail}: {stock!r} != {actual!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_CREATE_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Object bytes, return, buffer bytes and cleanup calls for five outcomes",
               "limits": ["Heap, mutex, and buffer constructor effects remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
