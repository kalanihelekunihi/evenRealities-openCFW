#!/usr/bin/env python3
"""Compare native animation cancel list operations with compiled C."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_cancel_450a74.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-cancel-450a74"
LOWER=[("first",0x482cd8,"audio_uart_lv_list_first"),
       ("next",0x482cf0,"audio_uart_lv_list_next"),
       ("remove",0x482c0e,"audio_uart_lv_list_remove"),
       ("free",0x44f758,"audio_uart_lv_heap_free"),
       ("schedule",0x4509da,"audio_uart_lv_transition_schedule_4509da")]
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_state[512];
void *audio_uart_lv_list_first(void *p){return 0;}
void *audio_uart_lv_list_next(void *p,void *n){return 0;}
void audio_uart_lv_list_remove(void *p,void *n){}
void audio_uart_lv_heap_free(void *p){}
void audio_uart_lv_transition_schedule_4509da(void){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_cancel_matching_450a74",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,input_mode,node_mode,count):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            root=(syms["audio_uart_display_lv_state"]+0xac) if compiled else 0x2006f5f4
            desc=0x20010000
            nodes=[0x20011000,0x20011100][:count]
            def write_word(address,offset,value):u.mem_write(address+offset,value.to_bytes(4,"little"))
            write_word(desc,0,0x20013000)
            write_word(desc,4,0x100001 if input_mode==2 else 0)
            write_word(desc,8,0x200001 if input_mode==1 else 0)
            for index,node in enumerate(nodes):
                write_word(node,0,0x20013000 if node_mode in (0,2) else 0x20014000)
                write_word(node,4,0x100001 if node_mode in (0,1,3) else 0x100003)
                write_word(node,0x14,0)
                write_word(node,0x34,0 if node_mode!=3 else 0xffffffff)
                u.mem_write(node+0x5c,bytes([0x10 if node_mode==3 else 0]))
                if index==1 and node_mode==0:write_word(node,0,0x20014000)
            active=list(nodes)
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            trace=[]
            def label(address):
                return "list" if address==root else "node0" if address==0x20011000 else \
                    "node1" if address==0x20011100 else hex(address)
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                r0=cpu.reg_read(A.UC_ARM_REG_R0)
                r1=cpu.reg_read(A.UC_ARM_REG_R1)
                if op=="first":
                    trace.append((op,label(r0)))
                    result=active[0] if active else 0
                elif op=="next":
                    trace.append((op,label(r0),label(r1)))
                    result=active[active.index(r1)+1] if r1 in active and active.index(r1)+1<len(active) else 0
                elif op=="remove":
                    trace.append((op,label(r0),label(r1)))
                    active.remove(r1)
                    result=0
                elif op=="free":
                    trace.append((op,label(r0)))
                    result=0
                else:
                    trace.append((op,))
                    result=0
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,desc)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms["audio_uart_lv_anim_cancel_matching_450a74"] if compiled else 0x450a74
            u.emu_start(origin|1,0x600000,count=100000)
            return trace,u.reg_read(A.UC_ARM_REG_R0),[label(n) for n in active]

        cases=list(itertools.product(range(3),range(4),range(3)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_CANCEL_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x450a74..0x450b0b",
             "cases":len(cases),"limits":["List helpers controlled; completion callback pointer absent.",
                                     "Live scheduler mutation remains unproved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
