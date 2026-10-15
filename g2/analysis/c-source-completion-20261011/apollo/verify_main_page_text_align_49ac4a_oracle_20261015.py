#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo line-alignment arithmetic."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_text_align_49ac4a.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-align-49ac4a"
SHIM='''#include <stdint.h>
int32_t audio_uart_text_width_4899a4(const char*t,uint32_t n,const void*f,int32_t s,uint32_t flags){(void)t;(void)n;(void)f;(void)s;(void)flags;return 0;}
int32_t audio_uart_lv_area_width_451598(const void*a){(void)a;return 0;}
'''
def put32(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get32(c,a):return int.from_bytes(c.mem_read(a,4),"little")
def signed(v):return v if v<0x80000000 else v-0x100000000
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf";shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_text_align_49ac4a",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            mode,old,width,available=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x400000)
            x,text,font,area=0x20011000,0x20012000,0x20013000,0x20014000
            put32(c,x,old);c.mem_write(text,b"abc\0");c.mem_write(area,bytes(0x20))
            sp=0x203ff000
            for i,v in enumerate((font,0xfffffffd,area,0x123456f8)):put32(c,sp+i*4,v)
            call_width=syms["audio_uart_text_width_4899a4"] if compiled else 0x4899a4
            call_area=syms["audio_uart_lv_area_width_451598"] if compiled else 0x451598
            trace=[]
            def hook(c,address,size,_):
                if address==(call_width&~1):
                    trace.append(("width",c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1),c.reg_read(A.UC_ARM_REG_R2),c.reg_read(A.UC_ARM_REG_R3),get32(c,c.reg_read(A.UC_ARM_REG_SP))))
                    c.reg_write(A.UC_ARM_REG_R0,width&0xffffffff)
                elif address==(call_area&~1):
                    trace.append(("area",c.reg_read(A.UC_ARM_REG_R0)))
                    c.reg_write(A.UC_ARM_REG_R0,available&0xffffffff)
                else:return
                c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            for reg,val in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),(x,mode,text,3)):c.reg_write(reg,val)
            c.reg_write(A.UC_ARM_REG_SP,sp);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((syms["audio_uart_page_text_align_49ac4a"] if compiled else 0x49ac4a)|1,0x600000,count=10000)
            return trace,signed(get32(c,x))
        cases=list(itertools.product((0,1,2,3,4,0x102,0x103),(0,11,-9),(0,7,-5),(0,21,-13)))
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_ALIGN_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_span":"0x49ac4a..0x49acad","cases":len(cases),"limits":["Text width and area width are controlled providers; live layout remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
