#!/usr/bin/env python3
"""Controlled native/C comparison of Apollo page-class event dispatch."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_class_event_49a16e.c"
OUT=G2/"build/c-firmware/20261015/main-page-class-event-49a16e"
HELPERS=(("base",0x4516f8,"audio_uart_lv_object_event_base_4516f8"),
         ("code",0x450286,"audio_uart_page_event_code_450286"),
         ("update",0x49a602,"audio_uart_page_layout_update_49a602"),
         ("metric0",0x4993c0,"audio_uart_page_metric_4993c0"),
         ("metric1",0x4993ca,"audio_uart_page_metric_4993ca"),
         ("metric2",0x4993d4,"audio_uart_page_metric_4993d4"),
         ("metric3",0x499360,"audio_uart_page_metric_499360"),
         ("metric4",0x49936a,"audio_uart_page_metric_49936a"),
         ("metric5",0x499374,"audio_uart_page_metric_499374"),
         ("content",0x43fe16,"audio_uart_lv_obj_content_width_43fe16"),
         ("prepare",0x49aacc,"audio_uart_page_event_prepare_49aacc"),
         ("calculate",0x489546,"audio_uart_page_event_calculate_489546"),
         ("finish",0x49ab06,"audio_uart_page_event_finish_49ab06"),
         ("extent",0x4519fa,"audio_uart_page_event_extent_4519fa"),
         ("dispatch",0x49a31c,"audio_uart_page_event_dispatch_49a31c"))
SHIM='''#include <stdint.h>
const uint8_t audio_uart_page_class_7561bc[36]={0};
uint32_t audio_uart_lv_object_event_base_4516f8(const void*c,void*e){(void)c;(void)e;return 0;}
uint32_t audio_uart_page_event_code_450286(void*e){(void)e;return 0;}
void audio_uart_page_layout_update_49a602(void*p){(void)p;}
const uint8_t*audio_uart_page_metric_4993c0(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_page_metric_4993ca(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_page_metric_4993d4(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_page_metric_499360(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_page_metric_49936a(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_page_metric_499374(void*p,uint32_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_lv_obj_content_width_43fe16(void*p){(void)p;return 0;}
void audio_uart_page_event_prepare_49aacc(void*p){(void)p;}
void audio_uart_page_event_calculate_489546(void*a,void*b,int32_t c,int32_t d,
    int32_t e,int32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
void audio_uart_page_event_finish_49ab06(void*p,int32_t n){(void)p;(void)n;}
void audio_uart_page_event_extent_4519fa(void*e,int32_t n){(void)e;(void)n;}
void audio_uart_page_event_dispatch_49a31c(void*e){(void)e;}
'''

def put32(cpu,address,value):cpu.mem_write(address,(value&0xffffffff).to_bytes(4,"little"))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    if int.from_bytes(blob[0x49ab9c-0x438000:0x49aba0-0x438000],"little")!=0x7561bc:
        raise RuntimeError("event class pointer literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_class_event_49a16e",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,case):
            base_result,code,flags,metric3,limit_mode,extent_seed=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            event,page,metric,extent=0x20010000,0x20011000,0x20014000,0x20015000
            cpu.mem_write(event,bytes([0xa5])*0x30)
            cpu.mem_write(page,bytes([0x11])*0x80)
            cpu.mem_write(extent,bytes([0x22])*0x10)
            put32(cpu,event,page);put32(cpu,event+0x10,extent)
            put32(cpu,page+0x2c,0x20016000)
            put32(cpu,page+0x34,0x12345678)
            put32(cpu,page+0x4c,20)
            put32(cpu,page+0x50,50)
            cpu.mem_write(page+0x5c,bytes([flags]))
            cpu.mem_write(page+0x2a,(0x800 if limit_mode else 0).to_bytes(2,"little"))
            put32(cpu,metric+0xc,0xfffffff9)
            put32(cpu,extent,extent_seed);put32(cpu,extent+4,extent_seed+5)
            targets={(syms[sym]&~1) if compiled else addr:name
                     for name,addr,sym in HELPERS}
            trace=[];metric4_count=metric5_count=0
            def hook(cpu,address,size,_):
                nonlocal metric4_count,metric5_count
                name=targets.get(address)
                if name is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                         A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if name=="base" and compiled and r0==syms["audio_uart_page_class_7561bc"]:
                    r0=0x7561bc
                if name=="calculate":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    extra=tuple(int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3))
                    trace.append((name,r0,r1,r2,r3,*extra))
                    put32(cpu,page+0x4c,27);put32(cpu,page+0x50,45)
                elif name in ("base","metric0","metric1","metric2","metric3","metric4",
                              "metric5","finish","extent"):
                    trace.append((name,r0,r1))
                else:trace.append((name,r0))
                value={"base":base_result,"code":code,"metric0":metric,
                       "metric1":13,"metric2":17,"metric3":metric3,"content":80}.get(name,0)
                if name=="metric4":
                    value=100 if metric4_count==0 else 70
                    metric4_count+=1
                if name=="metric5":
                    value=40 if metric5_count==0 else 30
                    metric5_count+=1
                cpu.reg_write(A.UC_ARM_REG_R0,value)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,0x7561bc)
            cpu.reg_write(A.UC_ARM_REG_R1,event)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_class_event_49a16e"] if compiled else 0x49a16e
            cpu.emu_start(entry|1,0x600000,count=100000)
            return trace,bytes(cpu.mem_read(page,0x80)),bytes(cpu.mem_read(extent,0x10))

        cases=list(itertools.product((0,1),(0x31,0x32,0x1b,0x34,0x1d,0x99),
                                     (0,0x80,0xe0),(0x3fffffff,5),(0,1),(10,80)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:
                raise AssertionError((case,stock[0],source[0],
                                      [(i,a,b) for i,(a,b) in enumerate(zip(stock[1],source[1]))
                                       if a!=b][:12],stock[2],source[2]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_CLASS_EVENT_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x49a16e..0x49a2ef",
             "cases":len(cases),
             "limits":["Lower event and layout helpers are controlled; live helper mutations and event-system behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
