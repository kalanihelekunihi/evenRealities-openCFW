#!/usr/bin/env python3
"""Compare Apollo scroll dispatch and finish callback call/descriptor traces."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_dispatch_44e884.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-dispatch-44e884"
LOWER=[("display",0x44dc0a,"audio_uart_lv_display_for_object"),
       ("init",0x4503d6,"audio_uart_lv_anim_init_4503d6"),
       ("width",0x44fa7e,"audio_uart_lv_display_width_44fa7e"),
       ("height",0x44faa8,"audio_uart_lv_display_height_44faa8"),
       ("duration",0x4505a2,"audio_uart_lv_anim_duration_clamp_4505a2"),
       ("values",0x4506ce,"audio_uart_lv_anim_values_4506ce"),
       ("start",0x450408,"audio_uart_lv_anim_start_450408"),
       ("event",0x451670,"audio_uart_lv_obj_event_451670"),
       ("x",0x44e486,"audio_uart_lv_obj_x_44e486"),
       ("y",0x44e498,"audio_uart_lv_obj_y_44e498"),
       ("unlink",0x450500,"audio_uart_lv_style_unlink_450500"),
       ("by",0x44ea98,"audio_uart_lv_scroll_by_44ea98")]
SHIM='''#include <stdint.h>
void *audio_uart_lv_display_for_object(void *p){return p;}
void audio_uart_lv_anim_init_4503d6(void *p){}
int32_t audio_uart_lv_display_width_44fa7e(void *p){return 600;}
int32_t audio_uart_lv_display_height_44faa8(void *p){return 400;}
int32_t audio_uart_lv_anim_duration_clamp_4505a2(int32_t x,int32_t a,int32_t b){return 250;}
void audio_uart_lv_anim_values_4506ce(void *p,int32_t a,int32_t b){}
void audio_uart_lv_anim_start_450408(void *p){}
void audio_uart_lv_anim_path_450672(void *p){}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t c,void *a){return 1;}
int32_t audio_uart_lv_obj_x_44e486(void *p){return -3;}
int32_t audio_uart_lv_obj_y_44e498(void *p){return 2;}
uint32_t audio_uart_lv_style_unlink_450500(void *p,void *f){return 0;}
uint32_t audio_uart_lv_scroll_by_44ea98(void *p,int32_t x,int32_t y){return 1;}
void audio_uart_lv_scroll_anim_x_44f3b8(void *p,int32_t v){}
void audio_uart_lv_scroll_anim_y_44f3d4(void *p,int32_t v){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_scroll_dispatch_44e884",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,x,y,animated,event_return,by_return,flag):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,display,desc=0x20010000,0x20012000,0x20013000
            if kind=="finish":
                u.mem_write(desc,obj.to_bytes(4,"little"))
                u.mem_write(desc+0x5c,bytes([flag]))
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]
            pointers={"x":(syms["audio_uart_lv_scroll_anim_x_44f3b8"]|1) if compiled else 0x44f3b9,
                      "y":(syms["audio_uart_lv_scroll_anim_y_44f3d4"]|1) if compiled else 0x44f3d5,
                      "finish":(syms["audio_uart_lv_scroll_anim_finish_44f3f0"]|1) if compiled else 0x44f3f1,
                      "path":(syms["audio_uart_lv_anim_path_450672"]|1) if compiled else 0x450673}
            def word(addr):return int.from_bytes(u.mem_read(addr,4),"little")
            def descriptor(addr):
                def pointer(value):
                    for label,target in pointers.items():
                        if value==target:return label
                    return hex(value)
                return (word(addr),pointer(word(addr+4)),pointer(word(addr+0x14)),
                        pointer(word(addr+0x20)),word(addr+0x30))
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                if op in ("init","start"):
                    trace.append((op,))
                elif op=="values":trace.append((op,regs[1],regs[2]))
                elif op=="event":
                    trace.append((op,regs[0],regs[1],
                                  descriptor(regs[2]) if regs[2] else None))
                elif op=="unlink":
                    trace.append((op,regs[0],
                                  "x" if regs[1]==pointers["x"] else
                                  "y" if regs[1]==pointers["y"] else hex(regs[1])))
                elif op=="duration":trace.append((op,*regs[:3]))
                elif op=="by":trace.append((op,*regs[:3]))
                else:trace.append((op,regs[0]))
                returns={"display":display,"width":600,"height":400,"duration":250,
                         "x":0xfffffffd,"y":2,"event":event_return,"by":by_return}
                cpu.reg_write(A.UC_ARM_REG_R0,returns.get(op,0))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,desc if kind=="finish" else obj)
            u.reg_write(A.UC_ARM_REG_R1,x)
            u.reg_write(A.UC_ARM_REG_R2,y)
            u.reg_write(A.UC_ARM_REG_R3,animated)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            name="audio_uart_lv_scroll_anim_finish_44f3f0" if kind=="finish" else \
                "audio_uart_lv_scroll_dispatch_44e884"
            start=syms[name] if compiled else (0x44f3f0 if kind=="finish" else 0x44e884)
            u.emu_start(start|1,0x600000,count=100000)
            return trace

        cases=[("dispatch",x,y,a,e,b,0) for (x,y),a,e,b in itertools.product(
            ((0,0),(1,0),(0,1),(3,5),(0xffffffff,0xfffffffe)),
            (0,1,0x100),(0,1,0x101),(0,1))]
        cases += [("finish",0,0,0,1,1,f) for f in (0,1,8,0xff)]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_DISPATCH_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x44e884..0x44e9b9","0x44f3f0..0x44f40b"],
             "cases":len(cases),"limits":["Twelve lower calls controlled; descriptor fields compared at event boundary.",
                                     "Animation scheduler internals remain unresolved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
