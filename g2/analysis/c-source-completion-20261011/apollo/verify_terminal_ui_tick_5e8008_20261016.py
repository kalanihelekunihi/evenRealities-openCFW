#!/usr/bin/env python3
"""Compare Terminal timer callback state and lower calls against stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_tick_5e8008.c"
HELPER = G2 / "components/audio/uart_thread_source_candidate/terminal_timer_expired_5e7ea4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-tick-5e8008"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_timer_state_20073c38[0x18];
uint8_t audio_terminal_ui_mode;
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t audio_terminal_encode_voice_input_5cec72(const uint8_t*p){(void)p;return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_td_counter_b_get(void){return 0;}
uint32_t audio_td_record_elapsed_get_59769c(uint32_t a,uint32_t*b){(void)a;(void)b;return 0;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e8124-0x438000:0x5e8128-0x438000], "little") != 0x20073c38 or \
            int.from_bytes(blob[0x5e8174-0x438000:0x5e8178-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Terminal tick stock pointers changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "tick-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "tick-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_tick_5e8008",
                    str(SOURCE), str(HELPER), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    stock_cuts = {0x45a568: "role", 0x4490cc: "tick", 0x43d0ce: "flags",
                  0x43c0e4: "zero", 0x5cec72: "voice", 0x5e43d2: "request",
                  0x5973dc: "session", 0x59769c: "elapsed"}
    compiled_cuts = {symbols[name] & ~1: kind for name, kind in (
        ("audio_uart_device_role_get", "role"),
        ("g2_flashdb_candidate_tick", "tick"),
        ("audio_log_flags", "flags"),
        ("audio_uart_buffer_zero", "zero"),
        ("audio_terminal_encode_voice_input_5cec72", "voice"),
        ("audio_terminal_request_display", "request"),
        ("audio_td_counter_b_get", "session"),
        ("audio_td_record_elapsed_get_59769c", "elapsed"))}

    def run(compiled, role, voice, asr, mode, elapsed_ok, same):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        timer = symbols["audio_terminal_ui_timer_state_20073c38"] if compiled else 0x20073c38
        mode_addr = symbols["audio_terminal_ui_mode"] if compiled else 0x2006e345
        memory = bytearray(b"\xa5"*0x18)
        memory[0] = voice
        memory[8] = asr
        memory[4:8] = struct.pack("<I", 99)
        memory[12:16] = struct.pack("<I", 99)
        memory[16:20] = struct.pack("<I", 0x1234 if same else 0x8888)
        memory[20:24] = struct.pack("<I", 20 if same else 0x9999)
        u.mem_write(timer, bytes(memory))
        u.mem_write(mode_addr, bytes((mode,)))
        cuts = compiled_cuts if compiled else stock_cuts
        trace = []
        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if kind == "role":
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "tick":
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, 100)
            elif kind == "flags":
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "zero":
                trace.append((kind, r1, r2))
                cpu.mem_write(r0, b"\0"*r1)
            elif kind == "voice":
                trace.append((kind, bytes(cpu.mem_read(r0, 1)).hex()))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "request":
                trace.append((kind, r0, r1))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "session":
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
            elif kind == "elapsed":
                trace.append((kind, r0))
                cpu.mem_write(r1, struct.pack("<I", 20 if elapsed_ok else 0))
                cpu.reg_write(A.UC_ARM_REG_R0, elapsed_ok)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_tick_5e8008"] if compiled else 0x5e8008
        u.emu_start(entry|1, 0x600000, count=20000)
        return bytes(u.mem_read(timer, 0x18)).hex(), trace

    cases = 0
    for role in (0, 1, 2):
        for voice in (0, 1):
            for asr in (0, 1):
                for mode in (0, 7):
                    for elapsed_ok in (0, 1):
                        for same in (False, True):
                            stock = run(False, role, voice, asr, mode, elapsed_ok, same)
                            selected = run(True, role, voice, asr, mode, elapsed_ok, same)
                            if stock != selected:
                                raise RuntimeError(f"Terminal tick mismatch {role=} {voice=} {asr=} "
                                                   f"{mode=} {elapsed_ok=} {same=}: "
                                                   f"{stock[1]} vs {selected[1]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_TICK_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "helper_source": str(HELPER.relative_to(ROOT)), "helper_source_sha256": sha(HELPER),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "role, timeout, mode and elapsed-record branches with state and lower-call trace",
              "limits": ["Enabled logging, lower-call effects, real tick/RTC, RAM aliasing and concurrency remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
