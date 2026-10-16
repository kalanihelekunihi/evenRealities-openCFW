#!/usr/bin/env python3
"""Compare the compiled EvenAI text-stream initializer with pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_init_text_stream_4e551e.c"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-init-text-stream"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_even_ai_text_stream_handle_20074c04;
uint32_t audio_text_stream_create_552b30(void) { return 0; }
uint32_t audio_log_flags(void) { return 0; }
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, initial, allocated, mode):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    state = sy["audio_even_ai_text_stream_handle_20074c04"] if compiled else 0x20074c04
    cpu.mem_write(state, initial.to_bytes(4, "little"))
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_text_stream_create_552b30": "create", "audio_log_flags": "flag",
             "audio_log_extended": "extended", "compressed_log_output": "compressed"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x552b30: "create", 0x43d0ce: "flag", 0x43d574: "extended",
              0x43ce9e: "compressed"})
    calls = []
    def cstring(pointer):
        return bytes(cpu.mem_read(pointer, 240)).split(b"\0", 1)[0].decode("ascii")
    def intercept(machine, pc, size, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        if kind == "extended":
            sp = machine.reg_read(UC_ARM_REG_SP)
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2)),
                          cstring(machine.reg_read(UC_ARM_REG_R3)),
                          int.from_bytes(machine.mem_read(sp, 4), "little"),
                          cstring(int.from_bytes(machine.mem_read(sp + 4, 4), "little"))))
        elif kind == "compressed":
            calls.append((kind, r0, cstring(machine.reg_read(UC_ARM_REG_R1)),
                          cstring(machine.reg_read(UC_ARM_REG_R2))))
        else:
            calls.append((kind,))
        machine.reg_write(UC_ARM_REG_R0, allocated if kind == "create" else mode if kind == "flag" else 0)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_even_ai_init_text_stream_4e551e"] if compiled else 0x4e551e
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return int.from_bytes(cpu.mem_read(state, 4), "little"), calls

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "init-text-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "init-text-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_even_ai_init_text_stream_4e551e",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for initial in (0, 0x20003000):
        for allocated in (0, 0x20004000):
            for mode in (0, 1, 2, 3, 4, 5, 6, 7):
                stock = run(payload, segments, sy, False, initial, allocated, mode)
                actual = run(payload, segments, sy, True, initial, allocated, mode)
                if stock != actual:
                    raise RuntimeError(f"initializer mismatch {(initial, allocated, mode)}: {stock!r} != {actual!r}")
                cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_EVEN_AI_INIT_TEXT_STREAM_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Handle state, allocator call, logger order and metadata",
               "limits": ["Allocator behavior and logger side effects remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
