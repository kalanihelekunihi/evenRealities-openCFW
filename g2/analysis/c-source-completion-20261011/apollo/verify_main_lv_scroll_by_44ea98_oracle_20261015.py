#!/usr/bin/env python3
"""Compare Apollo scroll-by calls, layer offsets, and return behavior with C."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_by_44ea98.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-by-44ea98"
LOWER=[("setup",0x43e1fa,"audio_uart_lv_obj_setup_layer_43e1fa"),
       ("children",0x44035e,"audio_uart_lv_obj_move_children_44035e"),
       ("event",0x451670,"audio_uart_lv_obj_event_451670"),
       ("size",0x440656,"audio_uart_display_size_changed")]
SHIM='''#include <stdint.h>
void audio_uart_lv_obj_setup_layer_43e1fa(void *p){}
void audio_uart_lv_obj_move_children_44035e(void *p,int32_t x,int32_t y,uint32_t s){}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t e,void *a){return 1;}
void audio_uart_display_size_changed(void *p){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_scroll_by_44ea98",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,dx,dy,event_result):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,spec=0x20010000,0x20011000
            u.mem_write(obj+8,spec.to_bytes(4,"little"))
            u.mem_write(spec+0x20,(0x12345678).to_bytes(4,"little"))
            u.mem_write(spec+0x24,(0x80000000).to_bytes(4,"little"))
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                arity={"setup":1,"children":4,"event":3,"size":1}[op]
                trace.append((op,*regs[:arity]))
                cpu.reg_write(A.UC_ARM_REG_R0,event_result if op=="event" else 0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj)
            u.reg_write(A.UC_ARM_REG_R1,dx)
            u.reg_write(A.UC_ARM_REG_R2,dy)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            start=syms["audio_uart_lv_scroll_by_44ea98"] if compiled else 0x44ea98
            u.emu_start(start|1,0x600000,count=100000)
            return trace, u.reg_read(A.UC_ARM_REG_R0),u.mem_read(spec+0x20,8).hex()

        cases=list(itertools.product((0,1,0xffffffff,0x80000000),
                                     (0,1,0xffffffff,0x80000000),(0,1,2,0x100)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_BY_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44ea98..0x44eaf1",
             "cases":len(cases),"limits":["Four lower calls controlled; state updates and return compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
