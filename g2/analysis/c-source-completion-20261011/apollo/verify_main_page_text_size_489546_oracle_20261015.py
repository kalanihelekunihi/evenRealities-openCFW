#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo LV text size calculation."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_size_489546.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-size-489546"
SHIM='''#include <stdint.h>
uint32_t audio_uart_text_line_length_4897fc(const char*t,uint32_t n,const void*f,
 int32_t s,int32_t w,uint32_t r,uint32_t flags)
{(void)t;(void)n;(void)f;(void)s;(void)w;(void)r;(void)flags;return 0;}
int32_t audio_uart_text_line_width_489934(const char*t,uint32_t n,const void*f,int32_t s)
{(void)t;(void)n;(void)f;(void)s;return 0;}
void audio_uart_lvgl_log(uint32_t l,const char*f,uint32_t n,const char*fn,const char*m,...)
{(void)l;(void)f;(void)n;(void)fn;(void)m;}
'''
def put32(cpu,a,v):cpu.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))

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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_event_calculate_489546",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            raw,flags,line_space,font_height,missing=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            text,font,out=0x20011000,0x20012000,0x20013000
            cpu.mem_write(text,raw+b"\x00"+bytes([0x5a])*20)
            cpu.mem_write(font,bytes([0x33])*0x30)
            put32(cpu,font+0xc,font_height)
            cpu.mem_write(out,bytes([0xa5])*16)
            targets={(syms[sym]&~1) if compiled else addr:name for name,addr,sym in (
                ("length",0x4897fc,"audio_uart_text_line_length_4897fc"),
                ("width",0x489934,"audio_uart_text_line_width_489934"),
                ("log",0x44d25c,"audio_uart_lvgl_log"))}
            trace=[];width_calls=0
            def hook(cpu,address,size,_):
                nonlocal width_calls
                name=targets.get(address)
                if name is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                         A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if name=="length":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    extra=tuple(int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3))
                    trace.append((name,r0,r1,r2,r3,*extra))
                    remain=bytes(cpu.mem_read(r0,16)).split(b"\x00",1)[0]
                    result=min(2,len(remain))
                elif name=="width":
                    trace.append((name,r0,r1,r2,r3))
                    result=5+r1*3+width_calls
                    width_calls+=1
                else:
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    extra=int.from_bytes(cpu.mem_read(sp,4),"little")
                    trace.append((name,r0,r1,r2,r3,extra))
                    result=0
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,out)
            cpu.reg_write(A.UC_ARM_REG_R1,0 if missing==1 else text)
            cpu.reg_write(A.UC_ARM_REG_R2,0 if missing==2 else font)
            cpu.reg_write(A.UC_ARM_REG_R3,2)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.mem_write(0x203ff000,(line_space&0xffffffff).to_bytes(4,"little")+
                (0x345).to_bytes(4,"little")+(flags).to_bytes(4,"little"))
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_event_calculate_489546"] if compiled else 0x489546
            cpu.emu_start(entry|1,0x600000,count=100000)
            return trace,bytes(cpu.mem_read(out,16))
        cases=list(itertools.product((b"",b"A",b"AB",b"ABC",b"A\n",b"A\r",b"ABCD"),
                                     (0,1),(0,3,0x7fffffff),(0,16,0x7fff),(0,)))
        cases += [(b"ABC",0,3,16,1),(b"ABC",0,3,16,2)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_SIZE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x489546..0x489651",
             "cases":len(cases),
             "limits":["Line break and width helpers are controlled; their full C bodies and live font behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
