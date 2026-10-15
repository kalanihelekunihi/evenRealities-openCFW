#!/usr/bin/env python3
"""Controlled native/C comparison for LV line-width accumulation."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_line_width_489934.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-line-width-489934"
SHIM='''#include <stdint.h>
void audio_uart_text_next_glyph_489b3c(const char*t,uint32_t*g,uint32_t*n,uint32_t*p)
{(void)t;(void)g;(void)n;(void)p;}
int32_t audio_uart_font_glyph_advance_4d57f4(const void*f,uint32_t g,uint32_t n)
{(void)f;(void)g;(void)n;return 0;}
'''
def put32(cpu,a,v):cpu.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get32(cpu,a):return int.from_bytes(cpu.mem_read(a,4),"little")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_line_width_489934",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            raw,length,spacing,missing=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            text,font=0x20011000,0x20012000
            cpu.mem_write(text,raw+b"\x00"+bytes([0x5a])*16)
            cpu.mem_write(font,bytes([0x33])*0x20)
            parser=syms["audio_uart_text_next_glyph_489b3c"] if compiled else 0x489b3c
            advance=syms["audio_uart_font_glyph_advance_4d57f4"] if compiled else 0x4d57f4
            trace=[]
            def hook(cpu,address,size,_):
                r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if address==(parser&~1):
                    glyph,nxt,pos=get32(cpu,r1),get32(cpu,r2),get32(cpu,r3)
                    trace.append(("parser",r0,glyph,nxt,pos))
                    ch=cpu.mem_read(r0+pos,1)[0]
                    put32(cpu,r1,ch)
                    put32(cpu,r2,cpu.mem_read(r0+pos+1,1)[0])
                    put32(cpu,r3,pos+1)
                    cpu.reg_write(A.UC_ARM_REG_R0,0)
                elif address==(advance&~1):
                    trace.append(("advance",r0,r1,r2))
                    result=0 if r1==ord('B') else (-2 if r1==ord('C') else 7)
                    cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
                else:return
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,0 if missing==1 else text)
            cpu.reg_write(A.UC_ARM_REG_R1,length)
            cpu.reg_write(A.UC_ARM_REG_R2,0 if missing==2 else font)
            cpu.reg_write(A.UC_ARM_REG_R3,spacing&0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_text_line_width_489934"] if compiled else 0x489934
            cpu.emu_start(entry|1,0x600000,count=100000)
            return trace,cpu.reg_read(A.UC_ARM_REG_R0)
        cases=[]
        for raw,spacing in itertools.product((b"",b"A",b"AB",b"ABC",b"A\n"),(-3,0,2)):
            for length in range(len(raw)+1):cases.append((raw,length,spacing,0))
        cases += [(b"ABC",3,2,1),(b"ABC",3,2,2)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_WIDTH_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x489934..0x4899a3",
             "cases":len(cases),
             "limits":["Glyph iterator and advance providers are controlled; full Unicode and font behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
