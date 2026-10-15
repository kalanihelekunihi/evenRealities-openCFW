#!/usr/bin/env python3
"""Compare Apollo display flush callback sequence with compiled C."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_callback_4736f4.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-4736f4"
LOWER = {
    "copy": (0x439c04, "audio_uart_display_area_copy_439c04"),
    "x": (0x44fb4e, "audio_uart_display_area_x_44fb4e"),
    "y": (0x44fb9a, "audio_uart_display_area_y_44fb9a"),
    "move": (0x450bb2, "audio_uart_ambiq_area_move_450bb2"),
    "cache": (0x48abb8, "audio_uart_lv_draw_flush_cache_48abb8"),
    "ready": (0x44fc42, "audio_uart_display_flush_ready_44fc42"),
    "begin": (0x47381e, "audio_uart_display_flush_begin_47381e"),
    "transfer": (0x47366c, "audio_uart_display_flush_transfer_47366c"),
    "end": (0x47386a, "audio_uart_display_flush_end_47386a"),
    "view": (0x474066, "audio_uart_display_flush_view_474066"),
}
SHIM = '''#include <stdint.h>
void *audio_uart_display_surface;
void *audio_uart_display_area_copy_439c04(void*p,const void*q,uint32_t n){return p;}
int32_t audio_uart_display_area_x_44fb4e(void*p){return 0;}
int32_t audio_uart_display_area_y_44fb9a(void*p){return 0;}
void audio_uart_ambiq_area_move_450bb2(void*p,int32_t x,int32_t y){}
void audio_uart_lv_draw_flush_cache_48abb8(void*p,uint32_t n){}
uint32_t audio_uart_display_flush_ready_44fc42(void*p){return 0;}
void audio_uart_display_flush_begin_47381e(void){}
void audio_uart_display_flush_transfer_47366c(uint32_t n,const void*p,uint32_t mode){}
void audio_uart_display_flush_end_47386a(void){}
void audio_uart_display_flush_view_474066(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x473908-0x438000:0x47390c-0x438000], "little") != 0x4736f5:
        raise RuntimeError("flush callback literal changed")
    if int.from_bytes(blob[0x4738fc-0x438000:0x473900-0x438000], "little") != 0x200746b4:
        raise RuntimeError("display surface literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_flush_callback_4736f4",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, ready, xpos, ypos):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            buffer, area, pixels, surface = 0x20010000, 0x20011000, 0x20012000, 0x20013000
            surface_cell = syms["audio_uart_display_surface"] if compiled else 0x200746b4
            u.mem_write(surface_cell, surface.to_bytes(4, "little"))
            u.mem_write(buffer + 0x30, (0x12345678).to_bytes(4, "little"))
            u.mem_write(area, bytes(range(16)))
            cuts = {(syms[name] & ~1) if compiled else address: kind
                    for kind, (address, name) in LOWER.items()}
            trace = []
            def label(value):
                return {buffer: "buffer", area: "area", pixels: "pixels", surface: "surface",
                        0: "null"}.get(value, hex(value))
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if kind == "copy":
                    trace.append((kind, label(r1), r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
                    result = r0
                elif kind in ("x", "y"):
                    trace.append((kind, label(r0)))
                    result = (xpos if kind == "x" else ypos) & 0xffffffff
                elif kind == "move":
                    trace.append((kind, tuple(cpu.mem_read(r0, 16)), r1, r2))
                    result = 0
                elif kind == "cache":
                    trace.append((kind, label(r0), r1))
                    result = 0
                elif kind == "ready":
                    trace.append((kind, label(r0)))
                    result = ready
                elif kind == "transfer":
                    trace.append((kind, r0, label(r1), r2))
                    result = 0
                elif kind == "view":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    e = int.from_bytes(cpu.mem_read(sp, 4), "little")
                    f = int.from_bytes(cpu.mem_read(sp + 4, 4), "little")
                    trace.append((kind, r0, r1, r2, r3, e, f))
                    result = 0
                else:
                    trace.append((kind,))
                    result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, buffer)
            u.reg_write(A.UC_ARM_REG_R1, area)
            u.reg_write(A.UC_ARM_REG_R2, pixels)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_display_flush_callback_4736f4"] if compiled else 0x4736f4) | 1,
                        0x600000, count=100000)
            return trace, int.from_bytes(u.mem_read(buffer + 0x30, 4), "little")
        cases = list(itertools.product((0, 1, 0x100, 0xffffffff), (0, 3, -4), (0, 2, -5)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x4736f4..0x473781",
               "native_callback_literal": "0x4736f5", "cases": len(cases),
               "limits": ["Display area, cache, transfer, and final view helpers controlled; live panel effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
