#!/usr/bin/env python3
"""Compare voice-input packet forwarding to pinned Terminal stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_voice_input_encode_5cec72.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-voice-input-encode-5cec72"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_message_sequence;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
uint32_t audio_terminal_send_message_5ce7c4(uint32_t a,uint32_t b,const void*c,uint32_t d,uint32_t e)
{(void)a;(void)b;(void)c;(void)d;(void)e;return 9;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5cf204-0x438000:0x5cf208-0x438000], "little") != 0x20074fff:
        raise RuntimeError("Terminal voice sequence stock pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "voice-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "voice-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_encode_voice_input_5cec72",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, present, command, sequence):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        seq_addr = symbols["audio_terminal_message_sequence"] if compiled else 0x20074fff
        u.mem_write(seq_addr, bytes((sequence,)))
        voice = 0x20001000
        u.mem_write(voice, bytes((command,)))
        flags = (symbols["audio_log_flags"] if compiled else 0x43d0ce)&~1
        send = (symbols["audio_terminal_send_message_5ce7c4"] if compiled else 0x5ce7c4)&~1
        trace = []
        def hook(cpu, pc, size, _):
            if pc == flags:
                trace.append(("flags",))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif pc == send:
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                fifth = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP), 4), "little")
                trace.append(("send", r0, r1, bytes(cpu.mem_read(r2, 1)).hex(), r3, fifth))
                cpu.reg_write(A.UC_ARM_REG_R0, 9)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, voice if present else 0)
        entry = symbols["audio_terminal_encode_voice_input_5cec72"] if compiled else 0x5cec72
        u.emu_start(entry|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for present in (False, True):
        for command in (0, 3, 0xff):
            for sequence in (0, 1, 0xfe, 0xff):
                stock, selected = run(False, present, command, sequence), \
                                  run(True, present, command, sequence)
                if stock != selected:
                    raise RuntimeError(f"voice input mismatch {present=} {command=} "
                                       f"{sequence=}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_VOICE_INPUT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "null and command packets, sequence wrap and lower send call",
              "limits": ["Enabled logging, lower protobuf/send effects and sequence startup remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
