#!/usr/bin/env python3
"""Compare stock LVGL speed packing, warning calls and C output."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_speed_4505a2.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-speed-4505a2"
SHIM='''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,const char *e,...){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_duration_clamp_4505a2",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,speed,min_time,max_time):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            cut=(syms["audio_uart_lvgl_log"]&~1) if compiled else 0x44d25c
            trace=[]
            def cstring(cpu,addr):
                chars=bytearray()
                for i in range(160):
                    ch=cpu.mem_read(addr+i,1)[0]
                    if ch==0:break
                    chars.append(ch)
                return chars.decode("utf8","replace")
            def hook(cpu,address,size,unused):
                if address!=cut:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                stack=cpu.reg_read(A.UC_ARM_REG_SP)
                fmt=int.from_bytes(cpu.mem_read(stack,4),"little")
                value=int.from_bytes(cpu.mem_read(stack+4,4),"little")
                trace.append((regs[0],cstring(cpu,regs[1]),regs[2],
                              cstring(cpu,regs[3]),cstring(cpu,fmt),value))
                cpu.reg_write(A.UC_ARM_REG_R0,0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),
                                 (speed,min_time,max_time)):u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms["audio_uart_lv_anim_duration_clamp_4505a2"] if compiled else 0x4505a2
            u.emu_start(origin|1,0x600000,count=100000)
            return trace,u.reg_read(A.UC_ARM_REG_R0)

        values=(0,1,4,5,200,9999,10000,10001,0xffffffff)
        cases=list(itertools.product(values,repeat=3))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_SPEED_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x4505a2..0x450633",
             "cases":len(cases),"limits":["Warning logger controlled; packed return compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
