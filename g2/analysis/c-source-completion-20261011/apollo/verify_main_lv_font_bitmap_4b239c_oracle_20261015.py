#!/usr/bin/env python3
"""Controlled stock/C bitmap callback comparison for the Apollo Main font."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_INVALID
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_font_bitmap_4b239c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-font-bitmap-4b239c"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_font_bitmap_stride(uint32_t w,uint8_t f){(void)f;return w+2;}
void audio_uart_lvgl_log(uint32_t l,const char *f,uint32_t n,const char *fn,const char *m)
{(void)l;(void)f;(void)n;(void)fn;(void)m;}
'''

def put32(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    native = blob[0x4b239c-0x438000:0x4b2690-0x438000]
    native_digest = hashlib.sha256(native).hexdigest()
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td)/"shim.c", Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_font_glyph_bitmap_4b239c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, case):
            width, height, bpp, packing, direct = case[:5]
            glyph_id = case[5] if len(case) == 6 else 1
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments: cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            glyph, font, state, table, bitmap, output = (
                0x20010000, 0x20010100, 0x20010200, 0x20010300, 0x20010400, 0x20011000)
            put32(cpu, glyph, font)
            put32(cpu, glyph+0x18, glyph_id)
            cpu.mem_write(glyph+0x14, bytes([direct]))
            put32(cpu, font+0x18, state)
            put32(cpu, state, bitmap)
            put32(cpu, state+4, table)
            cpu.mem_write(state+0x12, ((packing << 14) | (bpp << 9)).to_bytes(2,"little"))
            put32(cpu, table+16, 0x20)
            cpu.mem_write(table+16+8, width.to_bytes(2,"little")+height.to_bytes(2,"little"))
            cpu.mem_write(bitmap+0x20, bytes(((i*73+0xb5)&255) for i in range(128)))
            cpu.mem_write(output, bytes([0xa5])*128)
            put32(cpu, output+0x10, output+0x40)
            stride_symbol = syms["audio_uart_font_bitmap_stride"]
            target = stride_symbol if compiled else 0x48aad8
            log_target = syms["audio_uart_lvgl_log"] if compiled else 0x44d25c
            trace = []
            recent = []
            def hook(cpu, address, size, _):
                recent.append(address)
                if len(recent) > 12: recent.pop(0)
                if address == (log_target & ~1):
                    args = tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,
                        A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                    fifth = int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little")
                    trace.append(("log", *args, fifth))
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                    return
                if address != (target & ~1): return
                args = (cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1))
                trace.append(("stride", *args))
                cpu.reg_write(A.UC_ARM_REG_R0, args[0]+2)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            def invalid(cpu, access, address, size, value, _):
                raise RuntimeError((case, compiled, hex(cpu.reg_read(A.UC_ARM_REG_PC)),
                                    hex(address), access, size, hex(value)))
            cpu.hook_add(UC_HOOK_MEM_INVALID, invalid)
            cpu.reg_write(A.UC_ARM_REG_R0, glyph)
            cpu.reg_write(A.UC_ARM_REG_R1, output)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            try:
                cpu.emu_start((syms["audio_uart_lv_font_glyph_bitmap_4b239c"] if compiled
                               else 0x4b239c) | 1, 0x600000, count=300000)
            except Exception as error:
                raise RuntimeError((case, compiled, [hex(x) for x in recent],
                                    hex(cpu.reg_read(A.UC_ARM_REG_SP)), trace,
                                    [hex(cpu.reg_read(r)) for r in (A.UC_ARM_REG_R0,
                                     A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R8,
                                     A.UC_ARM_REG_R9)])) from error
            return trace, bytes(cpu.mem_read(output, 128)), cpu.reg_read(A.UC_ARM_REG_R0)

        cases = list(itertools.product((1, 3, 8, 9), (1, 2, 3), (1, 2, 4, 8),
                                       (0, 3), (0, 1)))
        cases += [(0, 2, 4, 0, 0), (3, 0, 4, 0, 0), (3, 2, 3, 0, 0)]
        cases += [(3, 2, 4, 1, 0), (3, 2, 4, 2, 0)]
        cases += [(3, 2, 4, 0, 0, 0)]
        for case in cases:
            stock, source = run(False, case), run(True, case)
            if stock != source:
                raise AssertionError((case, stock[0], source[0], stock[2], source[2],
                                      [(i,a,b) for i,(a,b) in enumerate(zip(stock[1],source[1]))
                                       if a != b][:12]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_FONT_BITMAP_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "native_span": "0x4b239c..0x4b268f", "native_sha256": native_digest,
               "cases": len(cases),
               "limits": ["Stride helper return controlled; real display allocation and device behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
