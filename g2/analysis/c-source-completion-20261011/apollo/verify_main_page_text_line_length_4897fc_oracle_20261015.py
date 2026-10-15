#!/usr/bin/env python3
"""Compare Apollo line-length C with native code using controlled callees."""
import hashlib, itertools, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_text_line_length_4897fc.c"
OUT = G2 / "build/c-firmware/20261015/main-page-text-line-length-4897fc"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_text_line_segment_489698(const char*t,const void*f,int32_t s,int32_t m,uint32_t g,int32_t*w,uint8_t*x){(void)t;(void)f;(void)s;(void)m;(void)g;(void)w;(void)x;return 0;}
uint32_t audio_uart_text_decode_489c5e(const char*t,uint32_t*n){(void)t;(void)n;return 0;}
int32_t audio_uart_font_glyph_advance_4d57f4(const void*f,uint32_t g,uint32_t n){(void)f;(void)g;(void)n;return 0;}
'''
def put32(c, a, v): c.mem_write(a, (v & 0xffffffff).to_bytes(4, "little"))
def get32(c, a): return int.from_bytes(c.mem_read(a, 4), "little")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_text_line_length_4897fc",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            raw, count, width, flags, missing, output, spacing = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for addr, data in segments: c.mem_write(addr, data)
            c.mem_map(0x20000000, 0x400000)
            text, font, out, sp = 0x20011000, 0x20012000, 0x20013000, 0x203ff000
            c.mem_write(text, raw + b"\x00" + bytes([0x5a])*16)
            c.mem_write(font, bytes([0x33])*0x20)
            put32(c, out, 0x12345678)
            segment = syms["audio_uart_text_line_segment_489698"] if compiled else 0x489698
            decode = syms["audio_uart_text_decode_489c5e"] if compiled else 0x489c5e
            advance = syms["audio_uart_font_glyph_advance_4d57f4"] if compiled else 0x4d57f4
            trace = []
            def hook(cpu, address, size, _):
                r0,r1,r2,r3 = (cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if address == (segment & ~1):
                    width_ptr = get32(cpu, sp-0x40) if False else None
                    # Stack arguments are at the callee's current SP, before its prologue.
                    callee_sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    f, w, scratch = (get32(cpu, callee_sp+i) for i in (0,4,8))
                    ch = cpu.mem_read(r0,1)[0]
                    consumed = 0 if ch == ord('!') else (2 if ch == ord('B') else 1)
                    used = 3 if consumed else 0
                    trace.append(("segment",r0,r1,r2,r3,f,w,scratch,ch))
                    put32(cpu,w,used)
                    cpu.reg_write(A.UC_ARM_REG_R0, consumed)
                elif address == (decode & ~1):
                    trace.append(("decode",r0,r1))
                    put32(cpu,r1,1)
                    cpu.reg_write(A.UC_ARM_REG_R0,cpu.mem_read(r0,1)[0])
                elif address == (advance & ~1):
                    trace.append(("advance",r0,r1,r2))
                    cpu.reg_write(A.UC_ARM_REG_R0,9)
                else: return
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, 0 if missing == 1 else text)
            c.reg_write(A.UC_ARM_REG_R1, count)
            c.reg_write(A.UC_ARM_REG_R2, 0 if missing == 2 else font)
            c.reg_write(A.UC_ARM_REG_R3, spacing & 0xffffffff)
            c.reg_write(A.UC_ARM_REG_SP, sp)
            put32(c,sp,width)
            put32(c,sp+4,out if output else 0)
            put32(c,sp+8,flags)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry = syms["audio_uart_text_line_length_4897fc"] if compiled else 0x4897fc
            c.emu_start(entry | 1,0x600000,count=100000)
            normalized = []
            for item in trace:
                normalized.append((item[0],) + tuple(
                    (v-text if text <= v < text+0x100 else
                     'font' if v == font else 'out' if v == out else
                     'ptr' if 0x20000000 <= v < 0x20400000 else v)
                    for v in item[1:]))
            return normalized,c.reg_read(A.UC_ARM_REG_R0),get32(c,out)
        cases=[]
        for raw,count,width,flags,output in itertools.product(
                (b"",b"A",b"AB",b"A\nB",b"A\rB",b"!B",b"BCA"),
                (0,1,4),(-1,0,2,20),(0,1,2,4),(False,True)):
            cases.append((raw,count,width,flags,0,output,2))
        cases += [(b"ABC",3,20,0,missing,True,0) for missing in (1,2)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock != source: raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_LENGTH_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x4897fc..0x489933",
             "cases":len(cases),"limits":["Segment, decoder, and glyph-advance providers are controlled; native callback cell is not yet source-owned."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__ == "__main__":main()
