#!/usr/bin/env python3
"""Compare Terminal output-start visual transition against pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_output_start_5e4920.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-output-start-5e4920"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_lv_obj_invalidate_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_processing_prepare_5ea30c(void){}
void audio_terminal_processing_hide_5e4878(uint32_t a){(void)a;}
void audio_lv_anim_start_49942e(uint32_t a,const uint32_t*b){(void)a;(void)b;}
void audio_terminal_elapsed_refresh_5e4902(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e53b4-0x438000:0x5e53b8-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "output-start-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "output-start-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_output_start_5e4920",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, missing, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        handles = [0x20001000, 0x20002000, 0x20003000, 0x20004000]
        for index, offset in enumerate((0x1cc, 0x1d0, 0x1d4, 0x1dc)):
            u.mem_write(state+offset, struct.pack("<I", 0 if index == missing else handles[index]))
        names = ("audio_lv_obj_invalidate_43dfa4",
                 "audio_terminal_processing_prepare_5ea30c",
                 "audio_terminal_processing_hide_5e4878",
                 "audio_lv_anim_start_49942e",
                 "audio_terminal_elapsed_refresh_5e4902",
                 "audio_log_flags", "audio_log_extended", "compressed_log_output")
        stock = (0x43dfa4, 0x5ea30c, 0x5e4878, 0x49942e,
                 0x5e4902, 0x43d0ce, 0x43d574, 0x43ce9e)
        cuts = {(symbols[name] if compiled else address)&~1: name
                for name, address in zip(names, stock)}
        trace = []

        def cstring(addr):
            out = bytearray()
            for i in range(128):
                ch = u.mem_read(addr+i, 1)[0]
                if ch == 0:
                    return out.decode("ascii")
                out.append(ch)
            raise RuntimeError("unterminated Terminal log string")

        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            if kind == "audio_lv_obj_invalidate_43dfa4":
                trace.append(("invalidate", r0, r1))
            elif kind == "audio_terminal_processing_prepare_5ea30c":
                trace.append(("prepare",))
            elif kind == "audio_terminal_processing_hide_5e4878":
                trace.append(("hide", r0))
            elif kind == "audio_lv_anim_start_49942e":
                trace.append(("animate", r0, r1 != 0,
                              int.from_bytes(u.mem_read(r1, 4), "little")))
            elif kind == "audio_terminal_elapsed_refresh_5e4902":
                trace.append(("refresh",))
            elif kind == "audio_log_flags":
                trace.append(("flags",))
                cpu.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "audio_log_extended":
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                message = cstring(int.from_bytes(u.mem_read(sp+4, 4), "little"))
                trace.append(("long", r0, message))
            else:
                trace.append(("short", r0, cstring(r1)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_output_start_5e4920"] if compiled else 0x5e4920
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for missing in (-1, 0, 1, 2, 3):
        for flags in (0, 1, 2, 4, 7):
            stock = run(False, missing, flags)
            selected = run(True, missing, flags)
            if stock != selected:
                raise RuntimeError(f"output-start mismatch {missing=} {flags=}: "
                                   f"{stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_OUTPUT_START_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "four-handle guard, lower-call order and arguments, zero-valued animation descriptor, five logging masks",
              "limits": ["Visual, animation, elapsed-refresh and logging sink child effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
