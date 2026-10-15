#!/usr/bin/env python3
"""Compare page layout mode and setter normal paths with the Apollo stock code."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_layout_499678.c"
OUT=G2/"build/c-firmware/20261015/main-page-layout-499678"
HELPERS=(("unlink",0x450500,"audio_uart_lv_style_unlink_450500"),
         ("update",0x49a602,"audio_uart_page_layout_update_49a602"),
         ("changed",0x440656,"audio_uart_display_size_changed"),
         ("log",0x44d25c,"audio_uart_lvgl_log"))
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_unlink_450500(void*p,void*s){(void)p;(void)s;return 0;}
void audio_uart_page_layout_update_49a602(void*p){(void)p;}
void audio_uart_display_size_changed(void*p){(void)p;}
void audio_uart_lvgl_log(uint32_t l,const char*f,uint32_t n,const char*fn,const char*m,...)
{(void)l;(void)f;(void)n;(void)fn;(void)m;}
'''

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    if tuple(int.from_bytes(blob[a-0x438000:a-0x438000+4],"little")
             for a in (0x49a134,0x49a2f0))!=(0x49abbd,0x49abc9):
        raise RuntimeError("layout setter pointer literals changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_layout_499678",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,operation,seed,flag,value):
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            page=0x20012000
            cpu.mem_write(page,bytes(((seed+i*29)&255) for i in range(0x80)))
            cpu.mem_write(page+0x5c,bytes([flag]))
            targets={(syms[sym]&~1) if compiled else addr:name
                     for name,addr,sym in HELPERS}
            trace=[]
            def hook(cpu,address,size,_):
                name=targets.get(address)
                if name is None:return
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                if name=="log":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    args=tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,
                         A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                    extra=tuple(int.from_bytes(cpu.mem_read(sp+i*4,4),"little")
                                for i in range(3))
                    trace.append(("log",*args,*extra))
                    cpu.emu_stop()
                    return
                if compiled and name=="unlink":
                    if r1==(syms["audio_uart_page_width_setter_49abbc"]|1):r1=0x49abbd
                    if r1==(syms["audio_uart_page_height_setter_49abc8"]|1):r1=0x49abc9
                trace.append((name,r0,r1 if name=="unlink" else None))
                cpu.reg_write(A.UC_ARM_REG_R0,0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            key={"layout":"audio_uart_page_layout_499678",
                 "null":"audio_uart_page_layout_499678",
                 "width":"audio_uart_page_width_setter_49abbc",
                 "height":"audio_uart_page_height_setter_49abc8"}[operation]
            native={"layout":0x499678,"null":0x499678,
                    "width":0x49abbc,"height":0x49abc8}[operation]
            cpu.reg_write(A.UC_ARM_REG_R0,0 if operation=="null" else page)
            cpu.reg_write(A.UC_ARM_REG_R1,value)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            cpu.emu_start((syms[key] if compiled else native)|1,0x600000,count=100000)
            return trace,bytes(cpu.mem_read(page,0x80)),
        layout=list(itertools.product(("layout",),(0,0x55),(0,0x40,0xff),
                                      (0,1,2,3,4,5,0x12,0xff)))
        setters=list(itertools.product(("width","height"),(0,0x55),(0,0x40,0xff),
                                       (0,1,0x12345678,0xffffffff)))
        cases=layout+setters+[("null",0,0,0)]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[0],source[0],
                                      [(i,a,b) for i,(a,b) in enumerate(zip(native[1],source[1]))
                                       if a!=b][:12]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,
             "native_spans":["0x499678..0x499715","0x49abbc..0x49abd3"],
             "cases":len(cases),
             "limits":["Normal page paths tested with controlled style unlink, update and invalidate helpers.",
                       "Null page log call matches stock; the subsequent fatal loop and actual lower-helper mutations remain unverified."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
