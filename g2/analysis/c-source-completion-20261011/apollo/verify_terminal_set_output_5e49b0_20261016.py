#!/usr/bin/env python3
"""Compare Terminal output-content transition with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_set_output_5e49b0.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-set-output-5e49b0"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint8_t audio_terminal_output_style_20003f80[8];
uint32_t audio_terminal_output_payload_20074a94;
uint8_t audio_terminal_output_mode_2007502d;
uint8_t audio_terminal_output_active_2007502c;
void audio_lv_obj_invalidate_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_processing_prepare_5ea30c(void){}
uint32_t audio_terminal_set_label_style_5e482a(uint32_t a,const void*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;return d;}
uint32_t audio_terminal_select_output_mode_5ea2a8(uint32_t a){(void)a;return 0;}
void audio_lv_anim_start_49942e(uint32_t a,const char*b){(void)a;(void)b;}
void audio_terminal_elapsed_refresh_5e4902(void){}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    for literal, value in ((0x5e53b4, 0x2006e0d0), (0x5e5558, 0x20003f80),
                           (0x5e555c, 0x20074a94), (0x5e5560, 0x2007502d),
                           (0x5e5564, 0x2007502c)):
        if int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") != value:
            raise RuntimeError(f"Terminal output literal {literal:#x} changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "set-output-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "set-output-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_set_output_5e49b0",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, missing, output, update, payload, active):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        handles = (0x20001000, 0x20002000, 0x20003000, 0x20004000)
        for index, offset in enumerate((0x1cc, 0x1d0, 0x1d4, 0x1dc)):
            u.mem_write(state+offset, struct.pack("<I", 0 if index == missing else handles[index]))
        style = symbols["audio_terminal_output_style_20003f80"] if compiled else 0x20003f80
        saved = symbols["audio_terminal_output_payload_20074a94"] if compiled else 0x20074a94
        mode = symbols["audio_terminal_output_mode_2007502d"] if compiled else 0x2007502d
        active_addr = symbols["audio_terminal_output_active_2007502c"] if compiled else 0x2007502c
        u.mem_write(style, b"ABCDEFGH")
        u.mem_write(saved, struct.pack("<I", 0xaaaaaaaa))
        u.mem_write(mode, b"\x23")
        u.mem_write(active_addr, bytes((active,)))
        names = ("audio_lv_obj_invalidate_43dfa4", "audio_terminal_processing_prepare_5ea30c",
                 "audio_terminal_set_label_style_5e482a", "audio_terminal_select_output_mode_5ea2a8",
                 "audio_lv_anim_start_49942e", "audio_terminal_elapsed_refresh_5e4902")
        stock = (0x43dfa4, 0x5ea30c, 0x5e482a, 0x5ea2a8, 0x49942e, 0x5e4902)
        cuts = {(symbols[name] if compiled else address)&~1: name
                for name, address in zip(names, stock)}
        trace = []

        def cstring(addr):
            out = bytearray()
            for i in range(80):
                ch = u.mem_read(addr+i, 1)[0]
                if ch == 0:
                    return out.decode("ascii")
                out.append(ch)
            raise RuntimeError("unterminated Terminal output text")

        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            if kind == names[0]:
                trace.append(("invalidate", r0, r1))
            elif kind == names[1]:
                trace.append(("prepare",))
            elif kind == names[2]:
                trace.append(("style", r0, r1 == style,
                              cpu.reg_read(A.UC_ARM_REG_R2), cpu.reg_read(A.UC_ARM_REG_R3)))
            elif kind == names[3]:
                trace.append(("mode", r0))
                cpu.reg_write(A.UC_ARM_REG_R0, 0x45)
            elif kind == names[4]:
                trace.append(("anim", r0, cstring(r1)))
            else:
                trace.append(("refresh",))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, output)
        u.reg_write(A.UC_ARM_REG_R1, update)
        u.reg_write(A.UC_ARM_REG_R2, payload)
        entry = symbols["audio_terminal_set_output_5e49b0"] if compiled else 0x5e49b0
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace, (bytes(u.mem_read(saved, 4)).hex(),
                       bytes(u.mem_read(mode, 1)).hex(),
                       bytes(u.mem_read(active_addr, 1)).hex())

    cases = 0
    for missing in (-1, 0, 1, 2, 3):
        for output, update in ((0, 0), (0, 1), (1, 0), (1, 1), (0x100, 0x100)):
            for active in (0, 1):
                for payload in (0, 0x12345678):
                    stock = run(False, missing, output, update, payload, active)
                    selected = run(True, missing, output, update, payload, active)
                    if stock != selected:
                        raise RuntimeError(f"set-output mismatch {missing=} {output=} "
                                           f"{update=} {active=} {payload=:#x}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SET_OUTPUT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "four-handle guard, output/update/active branch matrix, two payloads, lower-call order and RAM writes",
              "limits": ["LVGL and output-mode children, style RAM ownership and shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
