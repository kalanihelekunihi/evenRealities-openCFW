#!/usr/bin/env python3
"""Compare EvenAI common-timer stop RAM and logger calls against stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_4e2e62.c"
LINKER = G2 / "components/audio/uart_thread_source_candidate/even_ai_common_timer_ram.ld"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-common-timer-stop"
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

def run(payload, segments, sy, compiled, mode, seed):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for address, blob in segments:
        cpu.mem_write(address, blob)
    state = 0x20074008
    cpu.mem_write(state, seed)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_log_flags": "flag", "audio_log_extended": "extended",
             "compressed_log_output": "compressed"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x43d0ce: "flag", 0x43d574: "extended", 0x43ce9e: "compressed"})
    calls = []
    def cstring(p):
        return bytes(cpu.mem_read(p, 240)).split(b"\0", 1)[0].decode("ascii")
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
        machine.reg_write(UC_ARM_REG_R0, mode if kind == "flag" else 0)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_even_ai_common_timer_stop_4e2e86"] if compiled else 0x4e2e86
    cpu.emu_start(entry | 1, 0x600000, count=2000)
    return bytes(cpu.mem_read(state, 10)), calls

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "timer-stop-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "timer-stop-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,audio_even_ai_common_timer_stop_4e2e86",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    if sy["audio_even_ai_common_timer_state_20074008"] != 0x20074008:
        raise RuntimeError("timer RAM placement changed")
    cases = 0
    for mode in (0, 1, 2, 3, 4, 5, 6, 7):
        for seed in (bytes(10), bytes.fromhex("112233445566778899aa")):
            stock = run(payload, segments, sy, False, mode, seed)
            actual = run(payload, segments, sy, True, mode, seed)
            if stock != actual:
                raise RuntimeError(f"timer stop mismatch {mode=} {seed.hex()}: {stock!r} != {actual!r}")
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_EVEN_AI_COMMON_TIMER_STOP_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Stop RAM writes, logger call order, metadata and formats",
               "limits": ["Logger side effects and final whole-image placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
