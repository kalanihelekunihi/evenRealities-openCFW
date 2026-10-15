#!/usr/bin/env python3
"""Compare bounded animation scheduler start paths with Apollo native code."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_start_450408.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-start-450408"
LOWER=[("cancel",0x450a74,"audio_uart_lv_anim_cancel_matching_450a74"),
       ("list",0x482b12,"audio_uart_lv_list_prepend_482b12"),
       ("copy",0x454738,"audio_uart_lv_grid_copy_454738"),
       ("tick",0x473482,"audio_uart_lv_tick"),
       ("normalize",0x450a3e,"audio_uart_lv_anim_normalize_450a3e"),
       ("schedule",0x4509da,"audio_uart_lv_transition_schedule_4509da")]
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_state[512];
void audio_uart_lv_anim_cancel_matching_450a74(void *p){}
void *audio_uart_lv_list_prepend_482b12(void *p){return p;}
void *audio_uart_lv_grid_copy_454738(void *d,const void *s,uint32_t n){return d;}
uint32_t audio_uart_lv_tick(void){return 123;}
void audio_uart_lv_anim_normalize_450a3e(void *p){}
void audio_uart_lv_transition_schedule_4509da(void){}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,const char *e,...){}
uint32_t audio_uart_lv_anim_default_path_450634(void *p){return 77;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_start_450408",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,flag,state_bit,self_ref,active_path,seed):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            desc,allocated=0x20010000,0x20012000
            root=syms["audio_uart_display_lv_state"] if compiled else 0x2006f548
            u.mem_write(root+0xa5,bytes([state_bit]))
            source=bytearray(((seed+i*17)&0xff for i in range(96)))
            for offset in (4,8,0x18,0x20):source[offset:offset+4]=bytes(4)
            source[0:4]=(desc if self_ref else 0x20013000).to_bytes(4,"little")
            source[0x5c]=flag
            if active_path:
                pointer=(syms["audio_uart_lv_anim_default_path_450634"]|1) if compiled else 0x450635
                source[0x20:0x24]=pointer.to_bytes(4,"little")
            u.mem_write(desc,bytes(source))
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in LOWER}
            path_cut=(syms["audio_uart_lv_anim_default_path_450634"]&~1) if compiled else 0x450634
            trace=[]
            def hook(cpu,address,size,unused):
                if address==path_cut:
                    trace.append(("path",cpu.reg_read(A.UC_ARM_REG_R0)==allocated))
                    cpu.reg_write(A.UC_ARM_REG_R0,77)
                    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
                    return
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2)]
                if op=="list":trace.append((op,regs[0]==root+0xac))
                elif op=="copy":
                    trace.append((op,regs[0],regs[1],regs[2]))
                    cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])))
                elif op in ("cancel","normalize"):
                    trace.append((op,regs[0]==(desc if op=="cancel" else allocated)))
                else:trace.append((op,))
                cpu.reg_write(A.UC_ARM_REG_R0,allocated if op=="list" else 0x12345678 if op=="tick" else regs[0])
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,desc)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms["audio_uart_lv_anim_start_450408"] if compiled else 0x450408
            u.emu_start(origin|1,0x600000,count=100000)
            result=bytearray(u.mem_read(allocated,96))
            if active_path:
                expected=(syms["audio_uart_lv_anim_default_path_450634"]|1) if compiled else 0x450635
                if int.from_bytes(result[0x20:0x24],"little")!=expected:
                    raise AssertionError("animation path pointer changed")
                result[0x20:0x24]=bytes(4)
            return trace,u.reg_read(A.UC_ARM_REG_R0),bytes(result)

        cases=list(itertools.product((0,1,4,8,0x80,0x10),(0,1),(False,True),
                                     (False,True),(0,0x55)))
        cases=[case for case in cases if not (case[0]&0x10) or case[3]]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_START_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x450408..0x4504ff",
             "cases":len(cases),"limits":["Successful allocation; dynamic execution callbacks absent.",
                                     "Allocation failure and live scheduler behavior unproven."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
