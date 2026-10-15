#!/usr/bin/env python3
"""Compare Apollo LVGL scroll movement branch traces with compiled C."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_move_44e79e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-move-44e79e"
LOWER=[("page",0x43f66c,"audio_uart_page_43f66c"),
       ("x",0x44e486,"audio_uart_lv_obj_x_44e486"),
       ("y",0x44e498,"audio_uart_lv_obj_y_44e498"),
       ("mode",0x44e2a4,"audio_uart_lv_scroll_mode_44e2a4"),
       ("left",0x44e586,"audio_uart_lv_scroll_left_44e586"),
       ("right",0x44e67a,"audio_uart_lv_scroll_right_44e67a"),
       ("top",0x44e4aa,"audio_uart_lv_scroll_top_44e4aa"),
       ("bottom",0x44e4bc,"audio_uart_lv_scroll_bottom_44e4bc"),
       ("dispatch",0x44e884,"audio_uart_lv_scroll_dispatch_44e884")]
SHIM='''#include <stdint.h>
void audio_uart_page_43f66c(void *p){}
int32_t audio_uart_lv_obj_x_44e486(void *p){return 0;}
int32_t audio_uart_lv_obj_y_44e498(void *p){return 0;}
uint32_t audio_uart_lv_scroll_mode_44e2a4(void *p,uint32_t x){return 0;}
int32_t audio_uart_lv_scroll_left_44e586(void *p){return 0;}
int32_t audio_uart_lv_scroll_right_44e67a(void *p){return 0;}
int32_t audio_uart_lv_scroll_top_44e4aa(void *p){return 0;}
int32_t audio_uart_lv_scroll_bottom_44e4bc(void *p){return 0;}
void audio_uart_lv_scroll_dispatch_44e884(void *p,int32_t x,int32_t y,uint32_t a){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_scroll_move_44e79e",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,x,y,animated,mode,limits):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj=0x20010000
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]
            values={"x":0xfffffffd,"y":2,"mode":mode,"left":limits[0],
                    "right":limits[1],"top":limits[2],"bottom":limits[3]}
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                arity=4 if op=="dispatch" else 2 if op=="mode" else 1
                trace.append((op,*regs[:arity]))
                cpu.reg_write(A.UC_ARM_REG_R0,values.get(op,0))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,
                                  A.UC_ARM_REG_R3),(obj,x,y,animated)):
                u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            start=syms["audio_uart_lv_scroll_move_44e79e"] if compiled else 0x44e79e
            u.emu_start(start|1,0x600000,count=100000)
            return trace

        vectors=[(0,0),(1,0),(0,1),(0xffffffff,0),(0,0xffffffff),
                 (8,0xfffffffa),(0xfffffff0,0xfffffff0),(0x7fffffff,0x80000000),
                 (0x80000000,0x7fffffff)]
        limits=[(10,20,4,6),(0,0,0,0),(0x7fffffff,1,0x7fffffff,1)]
        cases=list(itertools.product(vectors,(0,1,0x100),(0,1),limits))
        for (x,y),animated,mode,limit in cases:
            case=(x,y,animated,mode,limit)
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MOVE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44e79e..0x44e883",
             "cases":len(cases),"limits":["Nine lower calls controlled; no full LVGL runtime proof."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
