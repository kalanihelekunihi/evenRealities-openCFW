#!/usr/bin/env python3
"""Compare Apollo object invalidate with controlled size, copy, and dispatch."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_invalidate_440656.c"
OUT=G2/"build/c-firmware/20261015/main-page-invalidate-440656"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_draw_size_get_452dc8(void*p){(void)p;return 0;}
void audio_uart_lv_area_copy_43ee94(void*d,const void*s){(void)d;(void)s;}
void audio_uart_display_invalidate_area(void*p,const int32_t*a){(void)p;(void)a;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_invalidate_440656",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            coords,size=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            obj=0x20011000;c.mem_write(obj,bytes([0x55])*0x80)
            for i,value in enumerate(coords):put(c,obj+0x14+i*4,value)
            lower=(("size",0x452dc8,"audio_uart_lv_draw_size_get_452dc8"),
                   ("copy",0x43ee94,"audio_uart_lv_area_copy_43ee94"),
                   ("invalidate",0x4405d4,"audio_uart_display_invalidate_area"))
            targets={syms[name]&~1 if compiled else native:(tag) for tag,native,name in lower}
            trace=[]
            def hook(cpu,address,amount,_):
                tag=targets.get(address)
                if tag is None:return
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                if tag=="size":
                    trace.append((tag,r0==obj))
                    cpu.reg_write(A.UC_ARM_REG_R0,size&0xffffffff)
                elif tag=="copy":
                    trace.append((tag,r1==obj+0x14))
                    cpu.mem_write(r0,bytes(cpu.mem_read(r1,16)))
                else:
                    trace.append((tag,r0==obj,tuple(get(cpu,r1+i*4) for i in range(4))))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,obj)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_invalidate_440656"] if compiled else 0x440656
            c.emu_start(entry|1,0x600000,count=10000)
            return trace
        patterns=((0,0,10,10),(-5,-7,5,7),(0x7fffffff,0x80000000,0,0),
                  (100,200,300,400))
        cases=list(itertools.product(patterns,(-2,0,1,7)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_INVALIDATE_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x440656..0x4406bb",
             "cases":len(cases),"limits":["Lower size, copy, and area invalidation providers are controlled; null assertion and live display effects remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
