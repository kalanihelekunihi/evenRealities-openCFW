#!/usr/bin/env python3
"""Compare Apollo redirect mutex initializer against the pinned stock body."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/file_redirect_init_474d9c.c"
OUT = G2 / "build/c-firmware/20261016/main-file-redirect-init"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void *g2_codec_redirect_mutex;
void *g2_codec_heap_mutex;
uint32_t audio_even_ai_mutex_create_44971c(const void*p){(void)p;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, first, second, mode):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    redirect_cell = sy["g2_codec_redirect_mutex"] if compiled else 0x200748f4
    heap_cell = sy["g2_codec_heap_mutex"] if compiled else 0x200748f8
    cpu.mem_write(redirect_cell, (0xdeadbeef).to_bytes(4, "little"))
    cpu.mem_write(heap_cell, (0xdeadbeef).to_bytes(4, "little"))
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_even_ai_mutex_create_44971c": "mutex", "audio_log_flags": "flag",
             "audio_log_extended": "extended", "compressed_log_output": "compressed"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x44971c: "mutex", 0x43d0ce: "flag", 0x43d574: "extended",
              0x43ce9e: "compressed"})
    calls = []
    mutex_count = 0
    def cstring(p):
        return bytes(cpu.mem_read(p, 240)).split(b"\0", 1)[0].decode("ascii")
    def intercept(machine, pc, width, unused):
        nonlocal mutex_count
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        if kind == "mutex":
            mutex_count += 1
            calls.append((kind, r0))
            returned = first if mutex_count == 1 else second
        elif kind == "extended":
            sp = machine.reg_read(UC_ARM_REG_SP)
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2)),
                          cstring(machine.reg_read(UC_ARM_REG_R3)),
                          int.from_bytes(machine.mem_read(sp, 4), "little"),
                          cstring(int.from_bytes(machine.mem_read(sp + 4, 4), "little"))))
            returned = 0
        elif kind == "compressed":
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2))))
            returned = 0
        else:
            calls.append((kind,))
            returned = mode
        machine.reg_write(UC_ARM_REG_R0, returned)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_file_redirect_init_474d9c"] if compiled else 0x474d9c
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return (cpu.reg_read(UC_ARM_REG_R0),
            int.from_bytes(cpu.mem_read(redirect_cell, 4), "little"),
            int.from_bytes(cpu.mem_read(heap_cell, 4), "little"), calls)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "redirect-init-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "redirect-init-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_file_redirect_init_474d9c",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for first in (0, 0x20003000):
        for second in (0, 0x20004000):
            for mode in range(8):
                stock = run(payload, segments, sy, False, first, second, mode)
                actual = run(payload, segments, sy, True, first, second, mode)
                if stock != actual:
                    raise RuntimeError(f"redirect mismatch {(first, second, mode)}: {stock!r} != {actual!r}")
                cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_FILE_REDIRECT_INIT_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Both mutex cells, returns and logger metadata across success/failure",
               "limits": ["Mutex creation and logger side effects, boot wiring remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
