#!/usr/bin/env python3
"""Controlled native/C comparison for LVGL object clean."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_clean_44d878.c"
OUT=G2/"build/c-firmware/20261015/main-page-clean-44d878"
SHIM='''#include <stdint.h>
void audio_uart_display_size_changed(void *p){}
uint32_t audio_uart_lv_child_count_44ddea(void *p){return 0;}
void *audio_uart_lv_first_live_child_44e164(void *p){return 0;}
void audio_uart_lv_child_delete_44df80(void *p){}
void audio_uart_lv_position_reset_44e9ba(void *p,uint32_t x,uint32_t y,uint32_t z){}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t c,void *a){return 1;}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
'''
LOWER=[("invalidate",0x440656,"audio_uart_display_size_changed"),
       ("count",0x44ddea,"audio_uart_lv_child_count_44ddea"),
       ("first",0x44e164,"audio_uart_lv_first_live_child_44e164"),
       ("delete",0x44df80,"audio_uart_lv_child_delete_44df80"),
       ("position",0x44e9ba,"audio_uart_lv_position_reset_44e9ba"),
       ("event",0x451670,"audio_uart_lv_obj_event_451670"),
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_44d878",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,present,has_layer,children,before,after):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,layer,child=0x20010000,0x20012000,0x20013000
            o=bytearray(64);o[8:12]=(layer if has_layer else 0).to_bytes(4,"little")
            l=bytearray(64);l[0x20:0x24]=(0x12345678).to_bytes(4,"little")
            l[0x24:0x28]=(0x87654321).to_bytes(4,"little")
            u.mem_write(obj,bytes(o));u.mem_write(layer,bytes(l))
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[];calls={"count":0,"first":0}

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
                                  *[read_string(p) for p in words]))
                    cpu.emu_stop();return
                trace.append((op,r0,r1 if op=="event" else 0,
                              (r1,r2,r3) if op=="position" else r2 if op=="event" else 0))
                result=0
                if op=="count":
                    result=before if calls["count"]==0 else after
                    calls["count"]+=1
                elif op=="first":
                    result=child if calls["first"]<children else 0
                    calls["first"]+=1
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj if present else 0)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_44d878"] if compiled else 0x44d878
            u.emu_start(entry|1,0x600000,count=100000)
            return (trace,bytes(u.mem_read(obj,64)),bytes(u.mem_read(layer,64)))

        cases=list(itertools.product((0,1),(0,1),(0,1,2),(0,1,2,3),(0,1,2,3)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[0],source[0],
                                      [a==b for a,b in zip(native[1:],source[1:])]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_CLEAN_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44d878..0x44d90d",
             "cases":len(cases),"limits":["Seven lower calls are controlled; child-deletion effects are modeled through count and selector returns.",
             "Null case stops at logger entry; logger internals and fatal loop unexecuted."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
