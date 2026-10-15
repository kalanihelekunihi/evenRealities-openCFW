#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo font glyph advance."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_font_glyph_advance_4d57f4.c"
OUT=G2/"build/c-firmware/20261015/main-page-font-glyph-advance-4d57f4"
SHIM='''#include <stdint.h>
uint32_t audio_uart_font_glyph_is_missing_4d559c(uint32_t g){(void)g;return 0;}
uint32_t audio_uart_font_glyph_describe_4d56c0(const void*f,void*d,uint32_t g,uint32_t n)
{(void)f;(void)d;(void)g;(void)n;return 0;}
'''
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_font_glyph_advance_4d57f4",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            glyph,next_glyph,missing=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            font=0x20011000;c.mem_write(font,bytes([0x45])*32)
            missing_fn=syms["audio_uart_font_glyph_is_missing_4d559c"] if compiled else 0x4d559c
            describe_fn=syms["audio_uart_font_glyph_describe_4d56c0"] if compiled else 0x4d56c0
            trace=[]
            def hook(cpu,address,size,_):
                r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if address==(missing_fn&~1):
                    trace.append(("missing",r0))
                    cpu.reg_write(A.UC_ARM_REG_R0,missing)
                elif address==(describe_fn&~1):
                    trace.append(("describe",r0,r2,r3))
                    cpu.mem_write(r1+4,b"\x34\x12")
                else:return
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,font)
            c.reg_write(A.UC_ARM_REG_R1,glyph)
            c.reg_write(A.UC_ARM_REG_R2,next_glyph)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_font_glyph_advance_4d57f4"] if compiled else 0x4d57f4
            c.emu_start(entry|1,0x600000,count=10000)
            return trace,c.reg_read(A.UC_ARM_REG_R0)
        cases=list(itertools.product((0,1,65,0xffff,0x10ffff),(0,66,0x1f600),(0,1)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_ADVANCE_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x4d57f4..0x4d5845",
             "cases":len(cases),"limits":["Missing-glyph and descriptor helpers are controlled; native null-font panic, live font records, kerning, and hardware rendering remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
