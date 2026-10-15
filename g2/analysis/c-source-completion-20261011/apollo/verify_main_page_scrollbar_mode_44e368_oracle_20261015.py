#!/usr/bin/env python3
"""Compare Apollo scrollbar-mode setter with the official payload."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_scrollbar_mode_44e368.c"
OUT=G2/"build/c-firmware/20261015/main-page-scrollbar-mode-44e368"
SHIM='''#include <stdint.h>
void audio_uart_lv_obj_setup_layer_43e1fa(void *p){}
void audio_uart_display_size_changed(void *p){}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
'''


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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_44e368",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,present,initial,mode):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000)
            u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,layer=0x20010000,0x20012000
            o,l=bytearray(64),bytearray(64)
            o[8:12]=layer.to_bytes(4,"little")
            l[0x32:0x34]=initial.to_bytes(2,"little")
            u.mem_write(obj,bytes(o));u.mem_write(layer,bytes(l))
            cuts={(syms[name]&~1) if compiled else addr: label for label,addr,name in
                  [("setup",0x43e1fa,"audio_uart_lv_obj_setup_layer_43e1fa"),
                   ("invalidate",0x440656,"audio_uart_display_size_changed"),
                   ("log",0x44d25c,"audio_uart_lvgl_log")]}
            trace=[]

            def read_string(ptr):return bytes(u.mem_read(ptr,128)).split(b"\0",1)[0].decode("utf8","replace")

            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                r0=cpu.reg_read(A.UC_ARM_REG_R0)
                if op=="log":
                    r1=cpu.reg_read(A.UC_ARM_REG_R1)
                    r2=cpu.reg_read(A.UC_ARM_REG_R2)
                    r3=cpu.reg_read(A.UC_ARM_REG_R3)
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    stack=[int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3)]
                    trace.append((op,r0,read_string(r1),r2,read_string(r3),
                                  *[read_string(p) for p in stack]))
                    cpu.emu_stop();return
                trace.append((op,r0))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj if present else 0)
            u.reg_write(A.UC_ARM_REG_R1,mode)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_44e368"] if compiled else 0x44e368
            u.emu_start(entry|1,0x600000,count=100000)
            return trace,bytes(u.mem_read(obj,64)),bytes(u.mem_read(layer,64)), \
                u.reg_read(A.UC_ARM_REG_R0) if present else None

        cases=list(itertools.product((0,1),(0,1,2,3,0x55aa),(0,1,2,3,4,0xff,0x100)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[0],source[0],
                                      [a==b for a,b in zip(native[1:],source[1:])]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_SCROLLBAR_MODE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44e368..0x44e3c9",
             "cases":len(cases),"limits":["Layer setup and invalidation are controlled.",
             "Null object case stops at logger entry; logger internals and fatal loop unexecuted."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
