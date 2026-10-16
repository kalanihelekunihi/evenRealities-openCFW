#!/usr/bin/env python3
"""Controlled stock/compiled comparison for EvenAI common and wrapper starts."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R3, UC_ARM_REG_R7, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_4e2e62.c"
LINKER = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_ram.ld"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-common-timer"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_uart_device_role_get(void) { return 0; }
uint32_t g2_kernel_candidate_os_get_tick(void) { return 0; }
void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t x) { (void)x; }
uint32_t audio_log_flags(void) { return 0; }
void audio_log_extended(uint8_t a, const char *b, const char *c, const char *d, uint32_t e, const char *f, ...) { (void)a;(void)b;(void)c;(void)d;(void)e;(void)f; }
uint32_t compressed_log_output(uint32_t a, const char *b, const char *c, ...) { (void)a;(void)b;(void)c;return 0; }
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, wrapper, role, duration, tick):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_write(0x438000, payload)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x20000000, 0x100000)
    for address, blob in segments:
        uc.mem_write(address, blob)
    state = 0x20074008
    seed = bytes.fromhex("112233445566778899aa")
    uc.mem_write(state, seed)
    uc.reg_write(UC_ARM_REG_R0, duration)
    uc.reg_write(UC_ARM_REG_R3, 0x13572468)
    uc.reg_write(UC_ARM_REG_R7, 0x24681357)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, 0x600001)
    hooks = ({0x45a568: ("role", role), 0x4490cc: ("tick", tick),
              0x4e304c: ("heartbeat", None)} if not compiled else
             {sy["audio_uart_device_role_get"] & ~1: ("role", role),
              sy["g2_kernel_candidate_os_get_tick"] & ~1: ("tick", tick),
              sy["audio_even_ai_heartbeat_timer_start_4e304c"] & ~1: ("heartbeat", None)})
    calls = []
    def hook(u, address, size, unused):
        if address not in hooks:
            return
        kind, value = hooks[address]
        calls.append((kind, u.reg_read(UC_ARM_REG_R0)))
        if value is not None:
            u.reg_write(UC_ARM_REG_R0, value)
        u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
    uc.hook_add(UC_HOOK_CODE, hook)
    name = "audio_even_ai_timer_start_all_4e31a0" if wrapper else "audio_even_ai_common_timer_start_4e2e62"
    addr = sy[name] if compiled else (0x4e31a0 if wrapper else 0x4e2e62)
    uc.emu_start(addr | 1, 0x600000, count=2000)
    return (bytes(uc.mem_read(state, 10)), calls, uc.reg_read(UC_ARM_REG_R0))

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "timer-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "timer-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-DOPENCFW_TIMER_START_ONLY",
                    "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,audio_even_ai_timer_start_all_4e31a0",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    if sy["audio_even_ai_common_timer_state_20074008"] != 0x20074008:
        raise RuntimeError("timer RAM placement changed")
    cases = 0
    for wrapper in (False, True):
        for role in (0, 1, 2):
            for duration in (0, 5000, 10000):
                for tick in (0, 0x12345678):
                    a = run(payload, segments, sy, False, wrapper, role, duration, tick)
                    b = run(payload, segments, sy, True, wrapper, role, duration, tick)
                    if a != b:
                        raise RuntimeError(f"timer mismatch {(wrapper, role, duration, tick)}: {a!r} != {b!r}")
                    cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_EVEN_AI_COMMON_TIMER_START_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Common timer and start-all: RAM, hook calls, ABI return",
               "limits": ["Common timer stop logging and whole-image placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
