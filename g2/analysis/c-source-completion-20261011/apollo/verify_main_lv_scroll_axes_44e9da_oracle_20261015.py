#!/usr/bin/env python3
"""Compare LVGL scroll-axis wrappers and transition callbacks with Apollo."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_axes_44e9da.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-axes-44e9da"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_unlink_450500(void *p,void *f){return 0;}
int32_t audio_uart_lv_obj_x_44e486(void *p){return 0;}
int32_t audio_uart_lv_obj_y_44e498(void *p){return 0;}
void audio_uart_lv_scroll_move_44e79e(void *p,int32_t x,int32_t y,uint8_t a){}
uint32_t audio_uart_lv_scroll_by_44ea98(void *p,int32_t x,int32_t y){return 1;}
'''
FUNS=[("x",0x44e9da,"audio_uart_lv_scroll_to_x_44e9da"),
      ("y",0x44ea04,"audio_uart_lv_scroll_to_y_44ea04"),
      ("callback_x",0x44f3b8,"audio_uart_lv_scroll_anim_x_44f3b8"),
      ("callback_y",0x44f3d4,"audio_uart_lv_scroll_anim_y_44f3d4")]
LOWER=[("unlink",0x450500,"audio_uart_lv_style_unlink_450500"),
       ("get_x",0x44e486,"audio_uart_lv_obj_x_44e486"),
       ("get_y",0x44e498,"audio_uart_lv_obj_y_44e498"),
       ("move",0x44e79e,"audio_uart_lv_scroll_move_44e79e"),
       ("by",0x44ea98,"audio_uart_lv_scroll_by_44ea98")]


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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_scroll_to_x_44e9da",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,value,animated):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj=0x20010000
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]

            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                if op=="unlink":
                    callback="audio_uart_lv_scroll_anim_x_44f3b8" if kind=="x" else \
                        "audio_uart_lv_scroll_anim_y_44f3d4"
                    expected=(syms[callback]|1) if compiled else \
                        (0x44f3b9 if kind=="x" else 0x44f3d5)
                    trace.append((op,regs[0],regs[1]==expected))
                elif op in ("get_x","get_y"):
                    trace.append((op,regs[0]))
                elif op=="move":
                    trace.append((op,*regs))
                else:
                    trace.append((op,*regs[:3]))
                cpu.reg_write(A.UC_ARM_REG_R0,
                              123 if op=="get_x" else 0xffffffd3 if op=="get_y" else 1)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj)
            u.reg_write(A.UC_ARM_REG_R1,value)
            u.reg_write(A.UC_ARM_REG_R2,animated)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            _,addr,name=next(row for row in FUNS if row[0]==kind)
            u.emu_start((syms[name] if compiled else addr)|1,0x600000,count=100000)
            return trace

        cases=list(itertools.product(("x","y","callback_x","callback_y"),
                                     (0,1,100,0xffffffff,0x80000000),
                                     (0,1,0xff,0x100)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_AXES_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x44e9da..0x44ea03","0x44ea04..0x44ea2d",
                             "0x44f3b8..0x44f3d1","0x44f3d4..0x44f3ed"],
             "cases":len(cases),"limits":["Five lower calls are controlled; callback pointer identity is checked.",
             "Scroll movement and scroll-by bodies remain unresolved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
