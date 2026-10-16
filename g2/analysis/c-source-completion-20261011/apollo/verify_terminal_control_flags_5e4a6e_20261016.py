#!/usr/bin/env python3
"""Compare Terminal trigger-bit handler with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_control_flags_5e4a6e.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-control-flags-5e4a6e"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
void audio_terminal_output_start_5e4920(void){}
void audio_terminal_set_output_5e49b0(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "control-flags-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "control-flags-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_control_flags_5e4a6e",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, trigger, payload, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        functions = {
            "flags": (symbols["audio_log_flags"] if compiled else 0x43d0ce)&~1,
            "long": (symbols["audio_log_extended"] if compiled else 0x43d574)&~1,
            "short": (symbols["compressed_log_output"] if compiled else 0x43ce9e)&~1,
            "start": (symbols["audio_terminal_output_start_5e4920"] if compiled else 0x5e4920)&~1,
            "set": (symbols["audio_terminal_set_output_5e49b0"] if compiled else 0x5e49b0)&~1}
        reverse = {addr: name for name, addr in functions.items()}
        trace = []

        def cstring(addr):
            out = bytearray()
            for i in range(128):
                ch = u.mem_read(addr+i, 1)[0]
                if ch == 0:
                    return out.decode("ascii")
                out.append(ch)
            raise RuntimeError("unterminated log string")

        def hook(cpu, pc, size, _):
            kind = reverse.get(pc)
            if kind is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            r2 = cpu.reg_read(A.UC_ARM_REG_R2)
            if kind == "flags":
                trace.append(("flags",))
                cpu.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "start":
                trace.append(("start",))
            elif kind == "set":
                trace.append(("set", r0, r1, r2))
            elif kind == "long":
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                message = cstring(int.from_bytes(u.mem_read(sp+4, 4), "little"))
                trace.append(("long", r0, message))
            else:
                trace.append(("short", r0, cstring(r1)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, trigger)
        u.reg_write(A.UC_ARM_REG_R1, payload)
        entry = symbols["audio_terminal_control_flags_5e4a6e"] if compiled else 0x5e4a6e
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for trigger in range(16):
        for payload in (0, 0x12345678, 0xffffffff):
            for flags in (0, 1, 2, 4, 7):
                stock = run(False, trigger, payload, flags)
                selected = run(True, trigger, payload, flags)
                if stock != selected:
                    raise RuntimeError(f"control flags mismatch {trigger=} {payload=:#x} "
                                       f"{flags=}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_CONTROL_FLAGS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "all 16 trigger masks, three payloads, five logging masks; lower-call and log sequence",
              "limits": ["Output-start/set child effects and actual logging sink effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
