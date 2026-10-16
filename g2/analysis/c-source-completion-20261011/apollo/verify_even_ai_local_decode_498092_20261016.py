#!/usr/bin/env python3
"""Compare compiled EvenAI local decode with stock on nonlogging state paths."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_local_decode_498092.c"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-local-decode"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
uint8_t audio_even_ai_service_state_2006ed10[0x218];
uint8_t audio_even_ai_config_state_20074974[3];
void audio_even_ai_state_lock_4e1fa6(void){}
void audio_even_ai_state_unlock_4e1fbe(void){}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){uint8_t *b=p;for(uint32_t i=0;i<n;i++)b[i]=(uint8_t)v;}
uint32_t audio_even_ai_encode_ctrl_4e3788(uint32_t x,const void *p){(void)x;(void)p;return 0;}
uint32_t audio_even_ai_encode_vad_4e3b80(uint32_t x,const void *p){(void)x;(void)p;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, symbols, compiled, data, length, log_mode):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_write(0x438000, payload)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x20000000, 0x100000)
    for addr, blob in segments:
        uc.mem_write(addr, blob)
    state = symbols["audio_even_ai_service_state_2006ed10"] if compiled else 0x2006ed10
    config = symbols["audio_even_ai_config_state_20074974"] if compiled else 0x20074974
    uc.mem_write(state, bytes([0xa5]) * 0x218)
    uc.mem_write(config, bytes([0x5a]) * 3)
    if data is not None:
        uc.mem_write(0x20003000, data + bytes(16))
    calls = []
    logs = []
    if compiled:
        hooks = {symbols[name] & ~1: name for name in (
            "audio_even_ai_state_lock_4e1fa6", "audio_even_ai_state_unlock_4e1fbe",
            "audio_uart_buffer_zero", "audio_even_ai_encode_ctrl_4e3788",
            "audio_even_ai_encode_vad_4e3b80", "audio_log_level",
            "audio_log_extended", "compressed_log_output")}
    else:
        hooks = {0x4e1fa6: "lock", 0x4e1fbe: "unlock", 0x43c0e4: "zero",
                 0x4982d4: "ctrl", 0x4982f2: "vad", 0x43d0ce: "log",
                 0x43d574: "extended", 0x43ce9e: "compressed"}
    def cstring(machine, pointer):
        return bytes(machine.mem_read(pointer, 240)).split(b"\0", 1)[0].decode("ascii")
    def intercept(machine, pc, size, unused):
        name = hooks.get(pc)
        if name is None:
            return
        if name in ("audio_uart_buffer_zero", "zero"):
            addr = machine.reg_read(UC_ARM_REG_R0)
            count = machine.reg_read(UC_ARM_REG_R1)
            value = machine.reg_read(UC_ARM_REG_R2)
            machine.mem_write(addr, bytes([value & 255]) * count)
        if name in ("audio_even_ai_encode_ctrl_4e3788", "ctrl",
                    "audio_even_ai_encode_vad_4e3b80", "vad"):
            if compiled:
                ptr = machine.reg_read(UC_ARM_REG_R1)
                calls.append(("ctrl" if "ctrl" in name else "vad", bytes(machine.mem_read(ptr, 2))))
            else:
                calls.append((name, bytes([machine.reg_read(UC_ARM_REG_R0) & 255, 0])))
        if name in ("audio_log_level", "log"):
            machine.reg_write(UC_ARM_REG_R0, log_mode)
        if name in ("audio_log_extended", "extended"):
            sp = machine.reg_read(UC_ARM_REG_SP)
            line = int.from_bytes(machine.mem_read(sp, 4), "little")
            fmt = cstring(machine, int.from_bytes(machine.mem_read(sp + 4, 4), "little"))
            value = int.from_bytes(machine.mem_read(sp + 8, 4), "little") if "%d" in fmt else None
            logs.append(("extended", machine.reg_read(UC_ARM_REG_R0),
                         cstring(machine, machine.reg_read(UC_ARM_REG_R1)),
                         cstring(machine, machine.reg_read(UC_ARM_REG_R2)),
                         cstring(machine, machine.reg_read(UC_ARM_REG_R3)), line, fmt, value))
        if name in ("compressed_log_output", "compressed"):
            fmt = cstring(machine, machine.reg_read(UC_ARM_REG_R1))
            value = machine.reg_read(UC_ARM_REG_R3) if "%d" in fmt else None
            logs.append(("compressed", machine.reg_read(UC_ARM_REG_R0), fmt, value))
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, intercept)
    uc.reg_write(UC_ARM_REG_R0, 0 if data is None else 0x20003000)
    uc.reg_write(UC_ARM_REG_R1, length)
    uc.reg_write(UC_ARM_REG_R2, 0x12345678)
    uc.reg_write(UC_ARM_REG_R3, 0x87654321)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, 0x600001)
    entry = symbols["audio_even_ai_local_decode_498092"] if compiled else 0x498092
    uc.emu_start(entry | 1, 0x600000, count=10000)
    return (uc.reg_read(UC_ARM_REG_R0), bytes(uc.mem_read(state, 0x30)),
            bytes(uc.mem_read(config, 3)), calls, logs)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "local-decode-oracle-stubs.c"
    stub.write_text(STUB)
    elf_path = OUT / "local-decode-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_even_ai_local_decode_498092",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = [
        (None, 0), (bytes([0]), 0), (bytes([9, 0, 1]), 3),
        (bytes([2, 1, 3, 0x11, 0x22, 0x33, 0x44, 7, 8, 9, 10]), 11),
        (bytes([2, 2, 0]), 3), (bytes([2, 3, 5]), 3),
        (bytes([2, 4, 0]), 3), (bytes([7, 6, 8]), 3)]
    for log_mode in (0, 1, 2, 4):
        for data, length in cases:
            native = run(payload, [], {}, False, data, length, log_mode)
            actual = run(payload, segments, symbols, True, data, length, log_mode)
            if native != actual:
                raise RuntimeError(f"EvenAI local decode mismatch {data!r} mode {log_mode}: {native!r} != {actual!r}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_EVEN_AI_LOCAL_DECODE_C_ORACLE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
        "oracle_elf_sha256": sha(elf_path), "cases": len(cases) * 4,
        "scope": "Return, first 0x30 state bytes, config bytes, notification arguments, and enabled log metadata and first values",
        "limits": ["Logger side effects, later variadic values, and nested notification encoder bodies are not covered.",
                   "No full-image placement or hardware execution is established."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], receipt["cases"], sha(path))

if __name__ == "__main__":
    main()
