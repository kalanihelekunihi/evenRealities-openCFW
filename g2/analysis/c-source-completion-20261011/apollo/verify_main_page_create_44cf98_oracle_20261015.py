#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo LVGL object construction."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_create_44cf98.c"
OUT=G2/"build/c-firmware/20261015/main-page-create-44cf98"
SHIM='''#include <stdint.h>
void *audio_uart_lv_heap_alloc(uint32_t n){return 0;}
void audio_uart_lv_heap_free(void *p){}
void *audio_uart_lv_realloc_44f76a(void *p,uint32_t n){return 0;}
void *audio_uart_display_default_get(void){return 0;}
uint32_t audio_uart_lv_display_width_44fa7e(void *p){return 0;}
uint32_t audio_uart_lv_display_height_44faa8(void *p){return 0;}
void audio_uart_lv_obj_setup_layer_43e1fa(void *p){}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
'''
LOWER=[("alloc",0x44f730,"audio_uart_lv_heap_alloc"),
       ("free",0x44f758,"audio_uart_lv_heap_free"),
       ("realloc",0x44f76a,"audio_uart_lv_realloc_44f76a"),
       ("display",0x44fa1a,"audio_uart_display_default_get"),
       ("width",0x44fa7e,"audio_uart_lv_display_width_44fa7e"),
       ("height",0x44faa8,"audio_uart_lv_display_height_44faa8"),
       ("layer",0x43e1fa,"audio_uart_lv_obj_setup_layer_43e1fa"),
       ("log",0x44d25c,"audio_uart_lvgl_log")]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_create_44cf98",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,parent_present,alloc_ok,display_ok,old_screens,inherited,realloc_ok):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            descriptor,base,page,parent,layer,display,array= (
                0x20010000,0x20010100,0x20012000,0x20013000,0x20014000,
                0x20015000,0x20016000)
            desc=bytearray(64)
            desc[0:4]=(base if inherited else 0).to_bytes(4,"little")
            desc[0x20:0x24]=(0 if inherited else 0x240).to_bytes(4,"little")
            u.mem_write(descriptor,bytes(desc))
            base_data=bytearray(64);base_data[0x20:0x24]=(0x240).to_bytes(4,"little")
            u.mem_write(base,bytes(base_data))
            u.mem_write(page,b"\0"*64)
            p=bytearray(64);p[8:12]=layer.to_bytes(4,"little")
            u.mem_write(parent,bytes(p))
            l=bytearray(64);l[0:4]=array.to_bytes(4,"little")
            l[0x30:0x32]=(1).to_bytes(2,"little")
            u.mem_write(layer,bytes(l))
            d=bytearray(0x300)
            d[0x2b8:0x2bc]=(array if old_screens else 0).to_bytes(4,"little")
            d[0x2d4:0x2d8]=(1).to_bytes(4,"little")
            u.mem_write(display,bytes(d));u.mem_write(array,b"\0"*64)
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]

            def read_string(ptr):return bytes(u.mem_read(ptr,160)).split(b"\0",1)[0].decode("utf8","replace")

            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in
                             (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if op=="log":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    words=[int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3)]
                    trace.append((op,r0,read_string(r1),r2,read_string(r3),
                                  read_string(words[0]),
                                  read_string(words[1]) if r0==3 else None,
                                  read_string(words[2]) if r0==3 else None))
                    if r0==3:
                        cpu.emu_stop();return
                else:
                    trace.append((op,r0,r1 if op=="realloc" else 0))
                result={"alloc":page if alloc_ok else 0,
                        "display":display if display_ok else 0,
                        "realloc":array if realloc_ok else 0,"width":320,"height":240}.get(op,0)
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,descriptor)
            u.reg_write(A.UC_ARM_REG_R1,parent if parent_present else 0)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_create_44cf98"] if compiled else 0x44cf98
            u.emu_start(entry|1,0x600000,count=100000)
            return (u.reg_read(A.UC_ARM_REG_R0),trace,bytes(u.mem_read(page,64)),
                    bytes(u.mem_read(parent,64)),bytes(u.mem_read(layer,64)),
                    bytes(u.mem_read(display,0x300)),bytes(u.mem_read(array,64)))

        cases=[case for case in itertools.product((0,1),(0,1),(0,1),(0,1),(0,1),(0,1))
               if not (case[0] and not case[5])]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[:2],source[:2],
                                      [a==b for a,b in zip(native[2:],source[2:])]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_CREATE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44cf98..0x44d0cf",
             "cases":len(cases),"limits":["Eight lower calls are controlled; allocator internals unexecuted.",
             "Root display-missing log, root-screen append, and child append are compared.",
             "Root reallocation failure stops at fatal logger entry; fatal loop remains unverified."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
