#!/usr/bin/env python3
"""Compare Apollo line segment C with native code and controlled glyph advance."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
DIR=G2/"components/audio/uart_thread_source_candidate"
SOURCES=[DIR/x for x in (
    "display_page_text_line_segment_489698.c",
    "display_page_text_decode_489c5e.c",
    "display_page_text_hash_state_489652.c",
    "display_page_text_break_char_4894a4.c",
    "display_page_text_cjk_4894d0.c")]
OUT=G2/"build/c-firmware/20261015/main-page-text-line-segment-489698"
SHIM='''#include <stdint.h>
int32_t audio_uart_font_glyph_advance_4d57f4(const void*f,uint32_t g,uint32_t n)
{(void)f;(void)g;(void)n;return 0;}
'''
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get(c,a):return int.from_bytes(c.mem_read(a,4),"little")
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_line_segment_489698",
                        *(str(x) for x in SOURCES),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            raw,spacing,max_width,flags,missing,output,initial_state=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for addr,data in segments:c.mem_write(addr,data)
            c.mem_map(0x20000000,0x400000)
            t,font,out,state,sp=0x20011000,0x20012000,0x20013000,0x20014000,0x203ff000
            c.mem_write(t,raw+b"\x00"*8)
            c.mem_write(font,bytes([0x33])*0x40)
            put(c,out,0x12345678)
            c.mem_write(state,bytes([initial_state]))
            advance=syms["audio_uart_font_glyph_advance_4d57f4"] if compiled else 0x4d57f4
            trace=[]
            def hook(cpu,address,size,_):
                if address!=(advance&~1):return
                r0,r1,r2=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
                trace.append((r0,r1,r2))
                value=0 if r1 in (0x20,0xa,0xd) else -2 if r1==0x23 else 7
                cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            for reg,value in ((A.UC_ARM_REG_R0,0 if missing==1 else t),
                              (A.UC_ARM_REG_R1,0 if missing==2 else font),
                              (A.UC_ARM_REG_R2,spacing&0xffffffff),
                              (A.UC_ARM_REG_R3,max_width&0xffffffff),
                              (A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x600001)):
                c.reg_write(reg,value)
            put(c,sp,flags)
            put(c,sp+4,out if output else 0)
            put(c,sp+8,state)
            entry=syms["audio_uart_text_line_segment_489698"] if compiled else 0x489698
            c.emu_start(entry|1,0x600000,count=100000)
            return trace,c.reg_read(A.UC_ARM_REG_R0),get(c,out),c.mem_read(state,1)[0]
        patterns=(b"",b"A",b"AB",b"A B",b"A,B",b"A\nB",b"A\r\nB",
                  b"#A",b"# A",b"A# B",b"\xe4\xb8\xadA",b"A\xe4\xb8\xadB")
        cases=list(itertools.product(patterns,(-2,0,2),(0,6,20),(0,4,8,12),(0,),(True,),(0,)))
        cases += [(b"ABC",0,20,0,m,True,0) for m in (1,2)]
        cases += [(b"ABC",0,20,0,0,False,0),
                  (b"# B",0,20,8,0,True,1),(b"# B",0,20,8,0,True,2)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_SEGMENT_ORACLE",
             "source":str(SOURCES[0].relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCES[0].read_bytes()).hexdigest(),
             "provider_source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES[1:]},
             "official_payload_sha256":digest,"native_span":"0x489698..0x4897f5",
             "cases":len(cases),"limits":["Glyph advance is controlled; non-CJK null-width dereference, extreme signed overflow, and live font behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
